# main.py
"""Main entry point for the AIObot application."""

import os

from dotenv import load_dotenv

from src.app import create_app
from src.constants import (
    OPENAI_API_KEY_ENV,
    PROJECT_NAME,
    TICKETMASTER_KEY_ENV,
    VERSION,
    WEATHERAPI_KEY_ENV,
)
from src.logger import logger


def main():
    """Run the AIObot application."""
    # Load environment variables
    load_dotenv(override=True)

    # Display version
    logger.info(f"🚀 Starting {PROJECT_NAME} v{VERSION}")

    # Validate required API keys
    required_keys = [OPENAI_API_KEY_ENV, WEATHERAPI_KEY_ENV, TICKETMASTER_KEY_ENV]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        logger.error("❌ Missing required API keys:")
        for key in missing_keys:
            logger.error(f"   - {key}")
        logger.info("💡 Please set these in your .env file")
        return

    logger.info("✅ All API keys loaded successfully")

    # Create and launch the application
    _, gradio_interface = create_app()
    gradio_interface.launch(server_port=7860, share=False)


if __name__ == "__main__":
    main()
