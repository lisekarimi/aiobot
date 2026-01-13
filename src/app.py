# src/app.py
"""Main application class that orchestrates all components."""

import asyncio

from src.api import TicketmasterAPI
from src.assistant_agent import ChatAssistant
from src.logger import logger
from src.ui import GradioInterface


class ActivityAssistant:
    """Main application class for the activity assistant."""

    def __init__(self):
        """Initialize the ActivityAssistant with event APIs and chat assistant."""
        logger.info("Initializing ActivityAssistant...")
        self.event_apis = {"ticketmaster": TicketmasterAPI()}
        self.chat_assistant = ChatAssistant()
        self._initialized = False
        logger.info("ActivityAssistant initialized successfully")

    async def initialize(self):
        """Initialize APIs and assistant."""
        if not self._initialized:
            await self.chat_assistant.initialize(self.event_apis)
            self._initialized = True
            logger.info("Assistant initialized")

    async def cleanup(self):
        """Cleanup resources."""
        if self._initialized:
            await self.chat_assistant.cleanup()
            logger.info("Resources cleaned up")

    def chat(self, user_message, history):
        """Process a chat message and yield responses.

        Args:
            user_message: The user's message
            history: Conversation history

        Yields:
            Response chunks from the assistant

        """
        logger.info(f"📨 Received user message: {user_message[:100]}...")

        # Ensure assistant is initialized
        if not self._initialized:
            logger.info("🔄 Assistant not initialized, initializing now...")
            asyncio.run(self.initialize())
            logger.info("✅ Assistant initialization complete")

        # Create event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            logger.info("🤖 Starting chat assistant processing...")

            # Create async generator
            async_gen = self.chat_assistant.chat(user_message, history)

            # Stream responses as they arrive
            chunk_count = 0
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    chunk_count += 1
                    logger.debug(f"📤 Yielding chunk {chunk_count}: {chunk[:50]}...")
                    yield chunk
                except StopAsyncIteration:
                    break

            logger.info(f"✅ Chat processing complete, streamed {chunk_count} chunks")
        finally:
            loop.close()


def create_app():
    """Create and return the application instance.

    Returns:
        Tuple of (ActivityAssistant, GradioInterface)

    """
    activity_assistant = ActivityAssistant()
    gradio_interface = GradioInterface(activity_assistant)
    return activity_assistant, gradio_interface
