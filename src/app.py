# src/app.py
"""Main application class that orchestrates all components."""

from src.api import TicketmasterAPI, WeatherAPI
from src.assistant import ChatAssistant
from src.logger import logger
from src.ui import GradioInterface


class ActivityAssistant:
    """Main application class for the activity assistant."""

    def __init__(self):
        """Initialize the activity assistant with all components."""
        logger.info("Initializing ActivityAssistant...")
        self.weather_api = WeatherAPI()
        self.event_apis = {"ticketmaster": TicketmasterAPI()}
        self.chat_assistant = ChatAssistant()
        logger.info("ActivityAssistant initialized successfully")

    def chat(self, user_message, history):
        """Process a chat message and yield responses.

        Args:
            user_message: The user's message
            history: Conversation history

        Yields:
            Response chunks from the assistant

        """
        response_stream = self.chat_assistant.chat(
            user_message, history, self.weather_api, self.event_apis
        )
        yield from response_stream


def create_app():
    """Create and return the application instance.

    Returns:
        Tuple of (ActivityAssistant, GradioInterface)

    """
    activity_assistant = ActivityAssistant()
    gradio_interface = GradioInterface(activity_assistant)
    return activity_assistant, gradio_interface
