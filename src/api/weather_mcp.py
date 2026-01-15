# src/api/weather_mcp.py
"""Weather service using Open-Meteo (free) with MCP server fallback."""

import os
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.api.weather import WeatherAPI
from src.logger import logger


class WeatherMCPService:
    """Weather service that uses Open-Meteo first (free), then MCP as fallback.

    Strategy:
    1. Try Open-Meteo API first (free, no API key required)
    2. If Open-Meteo fails and WEATHER_API_KEY exists, use MCP server (@swonixs/weatherapi-mcp)
    3. MCP server provides current weather with air quality data

    Note:
    - MCP fallback is only available for current weather (get_weather_current)
    - Forecasts and location search use Open-Meteo exclusively
    - MCP server runs via npx with Node.js (inter-process communication via stdio)

    This approach minimizes costs while maintaining reliability.

    """

    def __init__(self):
        """Initialize the WeatherMCPService with MCP server and fallback API."""
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.fallback_api = WeatherAPI()
        self._session = None
        logger.debug("WeatherMCPService initialized")

    @asynccontextmanager
    async def _get_mcp_session(self):
        """Get MCP session context manager using Node.js MCP server via npx."""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@swonixs/weatherapi-mcp"],
            env={"WEATHER_API_KEY": self.weather_api_key}
            if self.weather_api_key
            else {},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session

    async def get_weather_current(self, city: str, include_aqi: bool = False) -> dict:
        """Get current weather using Open-Meteo first, then MCP as fallback.

        Args:
            city: City name or location
            include_aqi: Whether to include air quality index (only available via MCP)

        Returns:
            Dictionary containing current weather data

        """
        # Try Open-Meteo first (free)
        logger.info(f"Fetching current weather from Open-Meteo (free) for {city}")
        weather_data = self.fallback_api.get_weather(city, days=1)

        if "error" not in weather_data:
            logger.info(f"Successfully fetched weather from Open-Meteo for {city}")
            return weather_data

        # If Open-Meteo fails and we have API key, try MCP
        if self.weather_api_key:
            logger.warning(f"Open-Meteo failed, trying MCP for {city}")
            try:
                async with self._get_mcp_session() as session:
                    result = await session.call_tool(
                        "get_weather",
                        arguments={"location": city},
                    )
                    logger.info(
                        f"Successfully fetched current weather from MCP for {city}"
                    )
                    return {"weather": result.content}

            except Exception as e:
                logger.error(f"Both Open-Meteo and MCP failed: {e}")
                return {
                    "error": f"All weather sources failed: {weather_data.get('error')}"
                }
        else:
            logger.error("Open-Meteo failed and no WEATHER_API_KEY for MCP fallback")
            return weather_data

    async def get_weather_forecast(self, city: str, days: int = 7) -> dict:
        """Get weather forecast using Open-Meteo (MCP fallback not available for forecasts).

        Args:
            city: City name or location
            days: Number of days to forecast (1-16)

        Returns:
            Dictionary containing weather forecast data

        Note:
            The @swonixs/weatherapi-mcp MCP server only provides current weather,
            so forecasts are only available via Open-Meteo.

        """
        logger.info(f"Fetching {days}-day forecast from Open-Meteo for {city}")
        weather_data = self.fallback_api.get_weather(city, days)

        if "error" not in weather_data:
            logger.info(f"Successfully fetched forecast from Open-Meteo for {city}")
            return weather_data
        else:
            logger.error(
                f"Failed to fetch forecast from Open-Meteo: {weather_data.get('error')}"
            )
            return weather_data

    async def search_location(self, query: str) -> dict:
        """Search for a location using Open-Meteo (MCP fallback not available for search).

        Args:
            query: Location search query

        Returns:
            Dictionary containing location search results

        Note:
            The @swonixs/weatherapi-mcp MCP server only provides current weather,
            so location search is only available via Open-Meteo.

        """
        logger.info(f"Searching location via Open-Meteo: {query}")
        coords = self.fallback_api._get_coordinates(query)

        if coords:
            logger.info(f"Successfully found location via Open-Meteo: {query}")
            return {"results": [{"name": query, "lat": coords[0], "lon": coords[1]}]}
        else:
            logger.error(f"Failed to find location via Open-Meteo: {query}")
            return {"error": "Location not found"}
