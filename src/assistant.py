# src/assistant.py
"""Chat assistant with OpenAI integration."""

import json
import os
from datetime import datetime

from openai import OpenAI

from src.constants import (
    DEFAULT_MODEL,
    MAX_ACTIVITIES,
    OPENAI_API_KEY_ENV,
    SYSTEM_PROMPT_TEMPLATE,
)
from src.logger import logger


class ChatAssistant:
    """Handles conversation with OpenAI and tool calls."""

    def __init__(self, model=DEFAULT_MODEL):
        """Initialize ChatAssistant.

        Args:
            model: OpenAI model to use

        """
        self.model = model
        self.openai = OpenAI(api_key=os.getenv(OPENAI_API_KEY_ENV))
        self.tools = self._define_tools()
        self.system_message = self._create_system_message()
        logger.debug(f"ChatAssistant initialized with model: {model}")

    def _create_system_message(self):
        """Create the system message for the assistant."""
        today_str = datetime.today().strftime("%Y-%m-%d")
        day_name = datetime.today().strftime("%A")

        return SYSTEM_PROMPT_TEMPLATE.format(
            nb_activity=MAX_ACTIVITIES, today_str=today_str, day_name=day_name
        )

    def _define_tools(self):
        """Define the tools available to the assistant."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather and forecast for the destination city.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The city for which the weather is being requested.",
                            },
                            "days": {
                                "type": "integer",
                                "description": "The number of days for the weather forecast (can be 1, 2, 6, or 10).",
                            },
                        },
                        "required": ["city", "days"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_ticketmaster_events",
                    "description": "Fetch upcoming events from Ticketmaster.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City where the events are searched.",
                            },
                            "country_code": {
                                "type": "string",
                                "description": "Country code for filtering results.",
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional keywords for event search (e.g., 'music', 'concert').",
                            },
                            "size": {
                                "type": "integer",
                                "description": "Number of events to fetch.",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date for the event search.",
                            },
                        },
                        "required": ["city", "country_code", "size", "start_date"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    def chat(self, user_message, history, weather_api, event_apis):
        """Process a chat message and yield streaming responses.

        Args:
            user_message: The user's message
            history: Conversation history
            weather_api: WeatherAPI instance
            event_apis: Dictionary of event API instances

        Yields:
            Streaming response chunks

        """
        # Build the conversation
        messages = (
            [{"role": "system", "content": self.system_message}]
            + history
            + [{"role": "user", "content": user_message}]
        )

        # OpenAI response
        response = self.openai.chat.completions.create(
            model=self.model, messages=messages, tools=self.tools, stream=True
        )

        recovered_pieces = {"content": None, "role": "assistant", "tool_calls": {}}
        last_tool_calls = {}
        has_tool_call = False
        result = ""

        for chunk in response:
            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason

            # Handle tool call detection
            if delta.tool_calls and finish_reason in [None, "tool_calls"]:
                has_tool_call = True
                piece = delta.tool_calls[0]

                # Create a dictionary for the tool call if it doesn't exist yet
                recovered_pieces["tool_calls"][piece.index] = recovered_pieces[
                    "tool_calls"
                ].get(
                    piece.index,
                    {
                        "id": None,
                        "function": {"arguments": "", "name": ""},
                        "type": "function",
                    },
                )

                if piece.id:
                    recovered_pieces["tool_calls"][piece.index]["id"] = piece.id
                if piece.function.name:
                    recovered_pieces["tool_calls"][piece.index]["function"]["name"] = (
                        piece.function.name
                    )
                recovered_pieces["tool_calls"][piece.index]["function"][
                    "arguments"
                ] += piece.function.arguments

                # Store the tool call in the dictionary by index
                last_tool_calls[piece.index] = recovered_pieces["tool_calls"][
                    piece.index
                ]

            # Store content in result and yield
            else:
                result += delta.content or ""
                if result.strip():
                    yield result

        # Handle tool call scenario
        if has_tool_call:
            # Handle the tool calls
            response = self._handle_tool_call(last_tool_calls, weather_api, event_apis)

            if response:
                tool_calls_list = [tool_call for tool_call in last_tool_calls.values()]
                messages.append({"role": "assistant", "tool_calls": tool_calls_list})

                # Dynamically process each tool call response
                for res in response:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": res["tool_call_id"],
                            "content": json.dumps(res["content"]),
                        }
                    )

            # New OpenAI request with tool response
            response = self.openai.chat.completions.create(
                model=self.model, messages=messages, stream=True
            )

            result = ""
            for chunk in response:
                result += chunk.choices[0].delta.content or ""
                if result.strip():
                    yield result

    def _handle_tool_call(self, tool_call, weather_api, event_apis):
        """Handle tool calls and return responses.

        Args:
            tool_call: Dictionary of tool calls
            weather_api: WeatherAPI instance
            event_apis: Dictionary of event API instances

        Returns:
            List of tool call responses

        """
        stored_values = {}

        for call in tool_call.values():
            arguments = json.loads(call["function"]["arguments"])

            for key, value in arguments.items():
                if key not in stored_values or stored_values[key] is None:
                    stored_values[key] = value

        city = stored_values.get("city")
        days = stored_values.get("days")
        country_code = stored_values.get("country_code")
        keywords = stored_values.get("keywords", [])
        start_date = stored_values.get("start_date")
        if start_date:
            start_date = str(start_date) + "T00:00:00Z"

        weather_data = None
        event_data = None

        # Iteration over tool_call
        for call in tool_call.values():
            if call["function"]["name"] == "get_weather":
                weather_data = weather_api.get_weather(city, days)

            if call["function"]["name"] == "get_ticketmaster_events":
                event_data = event_apis["ticketmaster"].get_events(
                    city, country_code, keywords, start_date
                )

        responses = []

        # Ensure weather response is always included
        weather_tool_call_id = next(
            (
                call["id"]
                for call in tool_call.values()
                if call["function"]["name"] == "get_weather"
            ),
            None,
        )
        if weather_data and "forecast" in weather_data:
            responses.append(
                {
                    "role": "assistant",
                    "content": {"weather": weather_data["forecast"]},
                    "tool_call_id": weather_tool_call_id,
                }
            )
        elif weather_tool_call_id:
            responses.append(
                {
                    "role": "assistant",
                    "content": {
                        "message": "No weather data available for this location."
                    },
                    "tool_call_id": weather_tool_call_id,
                }
            )

        # Ensure event response is always included
        event_tool_call_id = next(
            (
                call["id"]
                for call in tool_call.values()
                if call["function"]["name"] == "get_ticketmaster_events"
            ),
            None,
        )
        if event_data:
            responses.append(
                {
                    "role": "assistant",
                    "content": {"events": event_data},
                    "tool_call_id": event_tool_call_id,
                }
            )
        elif event_tool_call_id:
            responses.append(
                {
                    "role": "assistant",
                    "content": {"message": "No events found for this location."},
                    "tool_call_id": event_tool_call_id,
                }
            )

        return responses
