# src/api/weather.py
"""Weather API client using Open-Meteo (free, no API key required)."""

import requests

from src.logger import logger


class WeatherAPI:
    """Handles weather data fetching from Open-Meteo API (free fallback)."""

    def __init__(self):
        """Initialize the WeatherAPI with Open-Meteo endpoints."""
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    def _get_coordinates(self, city: str) -> tuple[float, float] | None:
        """Get latitude and longitude for a city.

        Args:
            city: City name

        Returns:
            Tuple of (latitude, longitude) or None if not found

        """
        try:
            response = requests.get(
                self.geocoding_url,
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                return result["latitude"], result["longitude"]
            return None
        except Exception as e:
            logger.error(f"Error getting coordinates for {city}: {e}")
            return None

    def get_weather(self, city: str, days: int = 7) -> dict:
        """Get weather forecast for a city using Open-Meteo (free).

        Args:
            city: City name
            days: Number of days to forecast (1-16)

        Returns:
            Dictionary containing weather data

        """
        logger.info(f"Fetching weather from Open-Meteo for {city} ({days} days)")

        # Get coordinates
        coords = self._get_coordinates(city)
        if not coords:
            return {"error": f"Could not find coordinates for {city}"}

        latitude, longitude = coords

        # Get weather data
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "weathercode",
                ],
                "current": [
                    "temperature_2m",
                    "weathercode",
                    "relative_humidity_2m",
                    "windspeed_10m",
                ],
                "timezone": "auto",
                "forecast_days": min(days, 16),
            }

            response = requests.get(self.weather_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Format the response
            result = {
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": data.get("timezone", "UTC"),
                "current": data.get("current", {}),
                "daily": data.get("daily", {}),
            }

            logger.info(f"Successfully fetched weather from Open-Meteo for {city}")
            return result

        except Exception as e:
            logger.error(f"Error fetching weather data from Open-Meteo: {e}")
            return {"error": str(e)}
