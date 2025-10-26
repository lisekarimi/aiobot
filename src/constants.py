# src/constants.py
"""Application constants and configuration."""

import tomllib
from pathlib import Path

# ==================== PROJECT METADATA ====================
_ROOT = Path(__file__).resolve().parent.parent
_SRC = Path(__file__).resolve().parent
with open(_ROOT / "pyproject.toml", "rb") as f:
    _pyproject = tomllib.load(f)

PROJECT_NAME = _pyproject["project"]["name"]
VERSION = _pyproject["project"]["version"]
DESCRIPTION = _pyproject["project"]["description"]

# API Configuration
DEFAULT_MODEL = "gpt-4o-mini"
WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"
TICKETMASTER_API_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

# API Keys Environment Variable Names
OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
WEATHERAPI_KEY_ENV = "WEATHERAPI_KEY"
TICKETMASTER_KEY_ENV = "TICKETMASTER_KEY"
PORT_ENV_VAR = "PORT"

# API Timeouts
API_TIMEOUT = 10  # seconds

# Activity Recommendations
MAX_ACTIVITIES = 10
MAX_FORECAST_DAYS = 14

# Ticketmaster Configuration
TICKETMASTER_EVENT_SIZE = 10

# Gradio UI Configuration
DEFAULT_SERVER_PORT = 7860
EXAMPLES_PER_PAGE = 6

# UI Text
APP_TITLE = "☀️ AIObot - Your Weather & Activity Assistant"
APP_HEADER = """
<div align="center">

# ☀️🏃‍♀️ AIObot - Your Weather & Activity Assistant

Get activity ideas based on today's weather and local events — just tell me your city!

🌍 Supported Countries for Events: 🇺🇸 US | 🇨🇦 CA | 🇬🇧 GB | 🇦🇺 AU | 🇦🇪 AE | 🇳🇴 NO | 🇳🇿 NZ
☀️ Weather data available globally!
</div>


"""

APP_FOOTER = f"""
---

<div style="background-color: #1e3a5f; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">

<a href="https://lisekarimi.com" target="_blank" style="display: inline-block; background-color: #2563eb; color: #ffffff !important; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: 500;">Portfolio</a>
<a href="https://github.com/lisekarimi/aiobot" target="_blank" style="display: inline-block; background-color: #2563eb; color: #ffffff !important; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: 500;">GitHub</a>

</div>

<div align="center">

{PROJECT_NAME} v{VERSION}

</div>
"""

# Load CSS from external file
_CSS_FILE = _SRC / "static" / "style.css"
with open(_CSS_FILE, encoding="utf-8") as f:
    APP_CSS = f.read()

# Example Prompts
EXAMPLE_PROMPTS = [
    ["What activities can I do in New York today?"],
    ["What can I do in Paris this weekend?"],
    ["I'm in London, what's the weather like and what events are happening?"],
]

# Supported Countries (ISO Alpha-2 Codes)
SUPPORTED_COUNTRIES = ["US", "CA", "GB", "AU", "AE", "NO", "NZ"]

# System Prompt Template
SYSTEM_PROMPT_TEMPLATE = """
You are a fun, helpful assistant for an Activity Suggestion App.
Recommend **up to {nb_activity} activities** based on real-time weather, balancing indoor, outdoor, and event-based options.

---

### **Core Rules**
- **Total limit**: 10 activities maximum (nb_events + nb_indoors + nb_outdoors ≤ 10)
- **One response**: Provide all suggestions at once—no waiting
- **Smart balancing**: Adjust mix based on weather, event availability, and user needs
- **Default date**: If no date specified, assume today

---

### **Date Interpretation**
Reference date: **{today_str} ({day_name})**
- "Tomorrow" = today + 1 day
- "Next Monday" = closest upcoming Monday
- "This weekend" = upcoming Saturday & Sunday
- Date ranges = calculate from today (e.g., "next 3 days" = today + 2)
- **Don't ask for confirmation**—interpret confidently

---

### **Process (All in One Go)**
1. **Get weather** for user's location and requested date
2. **Suggest activities** matching weather conditions
3. **Fetch events** from Ticketmaster (if available)
4. **Combine everything** into one structured response

---

### **Weather API**
- Calculate days offset for relative dates
- Show forecast only for requested date
- Limit: 14-day forecast (inform user if beyond range)
- If unavailable: notify in a friendly way

---

### **Ticketmaster API**
- Use ISO Alpha-2 country codes (FR, US, CA, DK, etc.)
- **Date mapping**:
  - "Today" → today's date
  - "Next Monday" → next occurrence of that day
  - "Next 3 days" → today as start date
- If >5 events found: ask for one-word interest (music, cinema, theater)
- If no events: inform user in a fun way
- **Never mention "Ticketmaster"**—just say "checking for events"

---

### **User Interaction**
- **No city provided?** → Ask for it
- **Event search fails?** → Say "no events found" (don't mention Ticketmaster)
- **Provide everything in one response**

---

### **Event Formatting**
When events are available:

Here are some events that may interest you:

**Event Name**:
- 📅 Date: 19th March 2025
- 📍 Venue: [venue name]
- 🔗 [Ticket Link](URL)

---

**Event Name**:
- 📅 Date: 19th March 2025
- 📍 Venue: [venue name]
- 🔗 [Ticket Link](URL)

---

### **Tone**
Be **short, fun, and accurate** with a dash of humor! Keep users smiling while delivering the best suggestions. 🎉
"""
