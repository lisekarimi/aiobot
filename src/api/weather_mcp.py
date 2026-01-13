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
    2. If Open-Meteo fails and WEATHER_API_KEY exists, use MCP server
    3. MCP server provides premium features (air quality, alerts, etc.)

    This approach minimizes costs while maintaining reliability.
    """

    def __init__(self):
        """Initialize the WeatherMCPService with MCP server path and fallback API."""
        self.mcp_server_path = "/opt/weather-mcp-server"
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.fallback_api = WeatherAPI()
        self._session = None
        logger.debug("WeatherMCPService initialized")

    @asynccontextmanager
    async def _get_mcp_session(self):
        """Get MCP session context manager."""
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", self.mcp_server_path, "run", "server.py"],
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
                        "weather_current",
                        arguments={"q": city, "aqi": "yes" if include_aqi else "no"},
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
        """Get weather forecast using Open-Meteo first, then MCP as fallback.

        Args:
            city: City name or location
            days: Number of days to forecast (1-16)

        Returns:
            Dictionary containing weather forecast data

        """
        # Try Open-Meteo first (free)
        logger.info(f"Fetching {days}-day forecast from Open-Meteo (free) for {city}")
        weather_data = self.fallback_api.get_weather(city, days)

        if "error" not in weather_data:
            logger.info(f"Successfully fetched forecast from Open-Meteo for {city}")
            return weather_data

        # If Open-Meteo fails and we have API key, try MCP
        if self.weather_api_key:
            logger.warning(f"Open-Meteo failed, trying MCP for {city}")
            try:
                async with self._get_mcp_session() as session:
                    result = await session.call_tool(
                        "weather_forecast",
                        arguments={"q": city, "days": min(days, 14)},
                    )
                    logger.info(f"Successfully fetched forecast from MCP for {city}")
                    return {"weather": result.content}

            except Exception as e:
                logger.error(f"Both Open-Meteo and MCP failed: {e}")
                return {
                    "error": f"All weather sources failed: {weather_data.get('error')}"
                }
        else:
            logger.error("Open-Meteo failed and no WEATHER_API_KEY for MCP fallback")
            return weather_data

    async def search_location(self, query: str) -> dict:
        """Search for a location using Open-Meteo first, then MCP as fallback.

        Args:
            query: Location search query

        Returns:
            Dictionary containing location search results

        """
        # Try Open-Meteo geocoding first (free)
        logger.info(f"Searching location via Open-Meteo (free): {query}")
        coords = self.fallback_api._get_coordinates(query)

        if coords:
            logger.info(f"Successfully found location via Open-Meteo: {query}")
            return {"results": [{"name": query, "lat": coords[0], "lon": coords[1]}]}

        # If Open-Meteo fails and we have API key, try MCP
        if self.weather_api_key:
            logger.warning(f"Open-Meteo geocoding failed, trying MCP for {query}")
            try:
                async with self._get_mcp_session() as session:
                    result = await session.call_tool(
                        "weather_search",
                        arguments={"q": query},
                    )
                    logger.info(f"Successfully searched location via MCP: {query}")
                    return {"results": result.content}

            except Exception as e:
                logger.error(f"Both Open-Meteo and MCP location search failed: {e}")
                return {"error": "Location not found in any source"}
        else:
            logger.error("Open-Meteo failed and no WEATHER_API_KEY for MCP fallback")
            return {"error": "Location not found"}
