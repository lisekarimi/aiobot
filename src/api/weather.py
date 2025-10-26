# src/api/weather.py
"""Weather API integration."""

import os

import requests

from src.constants import API_TIMEOUT, WEATHER_API_URL, WEATHERAPI_KEY_ENV
from src.logger import logger


class WeatherAPI:
    """Fetches weather data from WeatherAPI.com."""

    def __init__(self):
        """Initialize WeatherAPI with API key from environment."""
        self.api_key = os.getenv(WEATHERAPI_KEY_ENV)
        if not self.api_key:
            logger.error(f"❌ {WEATHERAPI_KEY_ENV} environment variable is required")
            raise ValueError(
                f"❌ {WEATHERAPI_KEY_ENV} environment variable is required"
            )
        logger.debug("WeatherAPI initialized successfully")

    def get_weather(self, city: str, days: int) -> dict:
        """Fetch weather data for the given city.

        Args:
            city: The city name to get weather for
            days: Number of days for forecast (1-14)

        Returns:
            Dictionary containing weather forecast data

        """
        params = {"key": self.api_key, "q": city, "days": days}

        logger.debug(f"Fetching weather for {city} for {days} days")
        response = requests.get(WEATHER_API_URL, params=params, timeout=API_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            forecast = []
            for day in data["forecast"]["forecastday"]:
                forecast.append({"date": day["date"], "temp": day["day"]["avgtemp_f"]})

            logger.info(f"Successfully fetched weather for {city}")
            return {"city": city, "forecast": forecast}
        else:
            logger.warning(
                f"Failed to fetch weather for {city}: {response.status_code}"
            )
            return {
                "error": f"City '{city}' not found or other issue. "
                "Please check the city name and try again."
            }
