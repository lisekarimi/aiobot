---
title: AIObot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
short_description: AI agent that suggests activities based on real-time weather
---

# 🤖 AIObot

A conversational AI agent that analyzes real-time weather conditions and suggests the best activities and events based on location. Whether it's sunny, rainy, or snowy, AIObot helps you make the most of your day!

🔗 **[Live Demo](https://aiobot.lisekarimi.com)**

![AIObot Screenshot](https://github.com/lisekarimi/aiobot/blob/main/assets/screenshot.png?raw=true)

## ✨ Features

- 🌤️ **Real-time Weather Analysis** - Get current weather conditions using Open-Meteo (free) with MCP fallback for premium features
- 🎯 **Personalized Activity Recommendations** - Indoor and outdoor activities based on weather
- 🎪 **Event Discovery** - Find relevant events using Ticketmaster API
- 💬 **Conversational Interface** - Chat with an AI assistant powered by OpenAI Agents SDK
- 🌍 **Global Coverage** - Works worldwide with weather data, events in select countries
- 🔄 **Smart Weather Fallback** - Automatically falls back to MCP/WeatherAPI when Open-Meteo is unavailable

## 🚀 Quick Start

### Prerequisites

- Python 3.11.x (not 3.12+)
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- WSL (Windows Subsystem for Linux)
- Make: `winget install GnuWin32.Make` (Windows) | `brew install make` (macOS) | `sudo apt install make` (Linux)

- API keys for:
  - [OpenAI](https://platform.openai.com/api-keys) (required)
  - [Ticketmaster](https://developer.ticketmaster.com) (required)
  - [WeatherAPI](https://www.weatherapi.com) (optional - used as fallback via MCP server)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lisekarimi/aiobot
   cd aiobot
   ```

2. **Set up environment variables**

   Create a `.env` file in the project root with your API keys:
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   TICKETMASTER_KEY=your_ticketmaster_key_here

   # Optional (for weather fallback via MCP)
   WEATHER_API_KEY=your_weatherapi_key_here
   ```

   **Note:** The app uses Open-Meteo (free) as the primary weather source. `WEATHER_API_KEY` is only needed if you want premium weather features (air quality, alerts) via the MCP fallback server.


### 🐋 Docker

Build and run with Docker:
```bash
make dev
```

## 🛠️ API Limitations & Weather Service

### Weather Service Strategy
The app uses a **dual-weather service approach** for reliability and cost efficiency:

1. **Primary:** [Open-Meteo](https://open-meteo.com/) - Free, no API key required, works globally
2. **Fallback:** MCP server with WeatherAPI - Used automatically if Open-Meteo fails (requires `WEATHER_API_KEY`)

This ensures the app always has weather data available, even if one service is down.

### Event API Limitations
- **Ticketmaster API** works primarily in English-speaking countries:
  - 🇺🇸 United States (US)
  - 🇨🇦 Canada (CA)
  - 🇬🇧 United Kingdom (GB)
  - 🇦🇺 Australia (AU)
  - 🇦🇪 Dubai, UAE (AE)
  - 🇳🇴 Norway (NO)
  - 🇳🇿 New Zealand (NZ)
- **Weather services** work globally for all locations
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

## 🌐 Deployment

This application is deployed on **AWS App Runner** with a dedicated CI/CD pipeline. The deployment workflow (`.github/workflows/deploy-aws.yml`) builds Docker images and pushes them to **AWS ECR** (Elastic Container Registry), from which AWS App Runner pulls and deploys the latest version of the application.
