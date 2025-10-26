# src/api/events.py
"""Event API integrations."""

import os
from abc import ABC, abstractmethod

import requests

from src.constants import (
    API_TIMEOUT,
    TICKETMASTER_API_URL,
    TICKETMASTER_EVENT_SIZE,
    TICKETMASTER_KEY_ENV,
)
from src.logger import logger


class BaseEventAPI(ABC):
    """Abstract base class for event APIs."""

    @abstractmethod
    def get_events(self, city, country_code, keywords, start_date):
        """Fetch upcoming events from an event provider.

        Args:
            city: City name
            country_code: ISO Alpha-2 country code
            keywords: List of search keywords
            start_date: Start date for event search

        Returns:
            List of event dictionaries

        """
        pass


class TicketmasterAPI(BaseEventAPI):
    """Fetches events from Ticketmaster API."""

    def __init__(self):
        """Initialize TicketmasterAPI with API key from environment."""
        self.api_key = os.getenv(TICKETMASTER_KEY_ENV)
        if not self.api_key:
            logger.error(f"❌ {TICKETMASTER_KEY_ENV} environment variable is required")
            raise ValueError(
                f"❌ {TICKETMASTER_KEY_ENV} environment variable is required"
            )
        logger.debug("TicketmasterAPI initialized successfully")

    def get_events(self, city, country_code, keywords, start_date):
        """Fetch upcoming events from Ticketmaster.

        Args:
            city: City name
            country_code: ISO Alpha-2 country code (e.g., US, GB, CA)
            keywords: List of search keywords
            start_date: Start date in ISO format with timezone (e.g., 2025-01-15T00:00:00Z)

        Returns:
            List of event dictionaries or error dict

        """
        params = {
            "apikey": self.api_key,
            "city": city,
            "countryCode": country_code,
            "keyword": ",".join(keywords) if keywords else None,
            "size": TICKETMASTER_EVENT_SIZE,
            "startDateTime": start_date,
        }

        logger.debug(f"Fetching events for {city}, {country_code}")
        response = requests.get(
            TICKETMASTER_API_URL, params=params, timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()
            events = data.get("_embedded", {}).get("events", [])
            event_list = (
                [
                    {
                        "name": event["name"],
                        "date": event["dates"]["start"]["localDate"],
                        "venue": event["_embedded"]["venues"][0]["name"],
                        "url": event.get("url", "N/A"),
                    }
                    for event in events
                ]
                if events
                else []
            )

            logger.info(f"Found {len(event_list)} events for {city}")
            return event_list
        else:
            logger.warning(f"Failed to fetch events for {city}: {response.status_code}")
            return {
                "error": f"API request failed! Status: {response.status_code}, "
                f"Response: {response.text}"
            }
