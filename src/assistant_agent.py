# src/assistant_agent.py
"""Chat assistant using OpenAI Agents SDK with function tools."""

import os
from datetime import datetime

from agents import Agent, Runner, function_tool

from src.api.weather_mcp import WeatherMCPService
from src.constants import (
    DEFAULT_MODEL,
    MAX_ACTIVITIES,
    OPENAI_API_KEY_ENV,
    SYSTEM_PROMPT_TEMPLATE,
)
from src.logger import logger


class ChatAssistant:
    """Handles conversation with OpenAI Agent and tool calls."""

    def __init__(self, model=DEFAULT_MODEL):
        """Initialize the ChatAssistant with model and weather service.

        Args:
            model: The OpenAI model to use (defaults to DEFAULT_MODEL)

        """
        self.model = model
        self.weather_service = (
            WeatherMCPService()
        )  # Open-Meteo first (free), MCP fallback
        self.event_apis = None  # Will be injected during initialize
        self.agent = None
        logger.debug(f"ChatAssistant initialized with model: {model}")

    async def initialize(self, event_apis):
        """Initialize APIs and create agent.

        Args:
            event_apis: Dictionary of event API instances

        """
        self.event_apis = event_apis
        self.agent = self._create_agent()
        logger.info("Agent created successfully")

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleanup complete")

    def _create_system_message(self):
        today_str = datetime.today().strftime("%Y-%m-%d")
        day_name = datetime.today().strftime("%A")

        return SYSTEM_PROMPT_TEMPLATE.format(
            nb_activity=MAX_ACTIVITIES, today_str=today_str, day_name=day_name
        )

    def _create_ticketmaster_tool(self):
        """Create Ticketmaster events tool using @function_tool decorator."""
        event_apis = self.event_apis

        @function_tool
        async def get_ticketmaster_events(
            city: str,
            country_code: str,
            size: int,
            start_date: str,
            keywords: list[str] | None = None,
        ) -> dict:
            """Fetch upcoming events from Ticketmaster.

            Args:
                city: City where the events are searched
                country_code: Country code for filtering results
                size: Number of events to fetch
                start_date: Start date for the event search (YYYY-MM-DD format)
                keywords: Optional keywords for event search (e.g., 'music', 'concert')

            Returns:
                Dictionary containing event data

            """
            logger.info(
                f"🎫 get_ticketmaster_events called for city: {city}, country: {country_code}, keywords: {keywords}"
            )

            if start_date:
                start_date = str(start_date) + "T00:00:00Z"

            try:
                event_data = event_apis["ticketmaster"].get_events(
                    city, country_code, keywords or [], start_date
                )

                if event_data:
                    logger.info(f"✅ Found {len(event_data)} events")
                    return {"events": event_data}
                else:
                    logger.warning(f"⚠️ No events found for {city}")
                    return {"message": "No events found for this location."}
            except Exception as e:
                logger.error(f"❌ Error fetching Ticketmaster events: {e}")
                return {"error": str(e)}

        return get_ticketmaster_events

    def _create_weather_tool(self):
        """Create weather tool using Open-Meteo (free) with MCP fallback."""
        weather_service = self.weather_service

        @function_tool
        async def get_weather(city: str, days: int = 7) -> dict:
            """Get the current weather and forecast for a city.

            Args:
                city: The city for which the weather is being requested
                days: The number of days for the weather forecast (1-14 days)

            Returns:
                Dictionary containing weather forecast data

            """
            logger.info(f"🌤️ get_weather called for city: {city}, days: {days}")

            try:
                # Uses Open-Meteo (free) first, then MCP as fallback if it fails
                weather_data = await weather_service.get_weather_forecast(city, days)

                if "error" in weather_data:
                    logger.error(f"❌ Weather fetch error: {weather_data['error']}")
                    return {"error": weather_data["error"]}

                logger.info(f"✅ Weather data received for {city}")
                return {"weather": weather_data}

            except Exception as e:
                logger.error(f"❌ Error fetching weather: {e}")
                return {"error": str(e)}

        return get_weather

    def _create_agent(self):
        """Create the OpenAI Agent with tools."""
        # Set OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = os.getenv(OPENAI_API_KEY_ENV)

        # Get system instructions
        instructions = self._create_system_message()

        # Create tools
        tools = [
            self._create_weather_tool(),
            self._create_ticketmaster_tool(),
        ]

        # Create agent
        agent = Agent(
            name="Activity Assistant",
            instructions=instructions,
            model=self.model,
            tools=tools,
        )

        logger.info(f"Agent created with model: {self.model}")
        return agent

    async def chat(self, user_message, history):
        """Process a chat message and yield streaming responses using Agent.

        Args:
            user_message: The user's message
            history: Conversation history (Gradio format)

        Yields:
            Streaming response chunks

        """
        logger.info(f"🧠 ChatAssistant processing message: {user_message[:100]}...")

        # Convert Gradio history to Agent format
        # Gradio messages format: [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]
        # Clean history to only include role and content (remove metadata that API doesn't accept)
        input_items = []
        if history:
            # Extract only role and content from each message
            input_items = [
                {"role": msg["role"], "content": msg["content"]} for msg in history
            ]

        # Add current user message
        input_items.append({"role": "user", "content": user_message})

        logger.info(f"📜 Conversation has {len(input_items)} messages")
        logger.info(f"🚀 Running OpenAI Agent with model: {self.model}")

        # Run agent with streaming
        result = Runner.run_streamed(
            self.agent,
            input=input_items,
            context=None,
        )

        logger.info("🔄 Streaming agent responses...")

        # Stream events and yield text deltas
        accumulated_text = ""
        event_count = 0
        async for event in result.stream_events():
            event_count += 1
            logger.debug(f"📊 Event #{event_count}: {type(event).__name__}")

            # Filter events by type to only show LLM text responses
            if hasattr(event, "data") and hasattr(event.data, "type"):
                event_type = event.data.type

                # Only yield user-facing text content
                if event_type == "response.output_text.delta":
                    accumulated_text += event.data.delta
                    logger.debug(
                        f"💬 Text delta received (total length: {len(accumulated_text)})"
                    )
                    yield accumulated_text

                # Filter out tool call arguments (these are internal)
                elif event_type in [
                    "response.function_call_arguments.delta",
                    "response.mcp_call_arguments.delta",
                    "response.custom_tool_call_input.delta",
                ]:
                    logger.debug(f"🔧 Filtering tool arguments: {event_type}")

            elif hasattr(event, "item") and hasattr(event.item, "output"):
                # Tool output - don't yield, just log
                logger.info(
                    f"🔧 Tool output received: {str(event.item.output)[:100]}..."
                )
            else:
                logger.debug(f"❓ Unknown event type: {event}")

        logger.info(
            f"✅ Streaming complete - {event_count} events, {len(accumulated_text)} chars"
        )

        # If no text was streamed, yield final output
        if not accumulated_text:
            logger.warning("⚠️ No text streamed, getting final output...")
            final_result = await result
            if final_result.final_output:
                logger.info(
                    f"✅ Got final output: {str(final_result.final_output)[:100]}..."
                )
                yield final_result.final_output
            else:
                logger.error("❌ No output from agent!")
