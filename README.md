# 🤖 AIObot

A conversational AI agent that analyzes real-time weather conditions and suggests the best activities and events based on location. Whether it's sunny, rainy, or snowy, AIObot helps you make the most of your day!

🔗 **[Live Demo](https://aiobot.lisekarimi.com)**

![AIObot Screenshot](https://github.com/lisekarimi/aiobot/blob/main/assets/screenshot.png?raw=true)

## ✨ Features

- 🌤️ **Real-time Weather Analysis** - Get current weather conditions for any location
- 🎯 **Personalized Activity Recommendations** - Indoor and outdoor activities based on weather
- 🎪 **Event Discovery** - Find relevant events using Ticketmaster API
- 💬 **Conversational Interface** - Chat with an AI assistant powered by OpenAI
- 🌍 **Global Coverage** - Works worldwide with weather data, events in select countries

## 🚀 Quick Start

### Prerequisites

- Python 3.11.x (not 3.12+)
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- WSL (Windows Subsystem for Linux)
- Make: `winget install GnuWin32.Make` (Windows) | `brew install make` (macOS) | `sudo apt install make` (Linux)

- API keys for:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [WeatherAPI](https://www.weatherapi.com)
  - [Ticketmaster](https://developer.ticketmaster.com)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lisekarimi/aiobot
   cd aiobot
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - OPENAI_API_KEY
   # - WEATHERAPI_KEY
   # - TICKETMASTER_KEY
   ```


### 🐋 Docker

Build and run with Docker:
```bash
make dev
```

## 🛠️ API Limitations

- **Ticketmaster API** works primarily in English-speaking countries:
  - 🇺🇸 United States (US)
  - 🇨🇦 Canada (CA)
  - 🇬🇧 United Kingdom (GB)
  - 🇦🇺 Australia (AU)
  - 🇦🇪 Dubai, UAE (AE)
  - 🇳🇴 Norway (NO)
  - 🇳🇿 New Zealand (NZ)
- **Weather API** works globally for all locations
- For other countries, the app will provide weather-based activity suggestions without events


## 🎯 Usage Examples

Try these example prompts:

- 💬 "What activities can I do in New York today?"
- 🌤️ "I'm in London, what's the weather like and what events are happening?"
- 🏠 "Suggest some indoor activities for Paris this weekend"
- ☀️ "What outdoor activities are good for sunny weather in Tokyo?"
- 🎪 "What can I do in Los Angeles this Saturday?"
- 🎵 "Show me music events in Toronto next week"

## Code Quality

```bash
# Run linting
make lint

# Fix code issues
make fix
```
