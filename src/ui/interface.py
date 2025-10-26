# src/ui/interface.py
"""Gradio interface for the application."""

import os

import gradio as gr

from src.constants import (
    APP_CSS,
    APP_FOOTER,
    APP_HEADER,
    APP_TITLE,
    DEFAULT_SERVER_PORT,
    EXAMPLE_PROMPTS,
    PORT_ENV_VAR,
)
from src.logger import logger


class GradioInterface:
    """Handles the Gradio UI for the activity assistant."""

    def __init__(self, activity_assistant):
        """Initialize the Gradio interface.

        Args:
            activity_assistant: ActivityAssistant instance

        """
        self.activity_assistant = activity_assistant
        logger.debug("GradioInterface initialized")

    def launch(self, share=False, server_port=None):
        """Launch the Gradio interface.

        Args:
            share: Whether to create a public link
            server_port: Port to run the server on (defaults to PORT env var or DEFAULT_SERVER_PORT)

        """
        # Get port from environment variable or use provided/default
        if server_port is None:
            server_port = int(os.getenv(PORT_ENV_VAR, DEFAULT_SERVER_PORT))

        logger.info(f"Launching Gradio interface on 0.0.0.0:{server_port}")

        with gr.Blocks(
            title=APP_TITLE,
            theme=gr.themes.Base(
                primary_hue="slate",
                secondary_hue="slate",
                neutral_hue="slate",
            ).set(
                body_background_fill="#1a1a1a",
                body_background_fill_dark="#1a1a1a",
                block_background_fill="#2d2d2d",
                block_background_fill_dark="#2d2d2d",
                block_label_background_fill="#2d2d2d",
                block_label_background_fill_dark="#2d2d2d",
                input_background_fill="#3a3a3a",
                input_background_fill_dark="#3a3a3a",
                button_primary_background_fill="#4a4a4a",
                button_primary_background_fill_dark="#4a4a4a",
                button_primary_background_fill_hover="#5a5a5a",
                button_primary_background_fill_hover_dark="#5a5a5a",
                button_primary_text_color="#ffffff",
                button_primary_text_color_dark="#ffffff",
                block_title_text_color="#ffffff",
                block_title_text_color_dark="#ffffff",
                block_label_text_color="#ffffff",
                block_label_text_color_dark="#ffffff",
                body_text_color="#ffffff",
                body_text_color_dark="#ffffff",
                input_placeholder_color="#999999",
                input_placeholder_color_dark="#999999",
            ),
            css=APP_CSS,
        ) as demo:
            # Header
            gr.Markdown(APP_HEADER)

            # Chat Interface
            gr.ChatInterface(
                fn=self.activity_assistant.chat,
                type="messages",
                examples=EXAMPLE_PROMPTS,
                cache_examples=False,
                chatbot=gr.Chatbot(height=800, type="messages"),
            )

            # Footer
            gr.Markdown(APP_FOOTER)

        demo.launch(
            share=share,
            server_port=server_port,
            server_name="0.0.0.0",
        )
