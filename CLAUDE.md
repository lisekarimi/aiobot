# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIObot is a conversational AI agent that analyzes real-time weather conditions and suggests activities and events based on location. Built with Python 3.11, OpenAI Agents SDK, and Gradio for the UI.

**Live Demo**: https://aiobot.lisekarimi.com

## Development Setup

### Prerequisites
- Python 3.11.x (not 3.12+)
- uv package manager
- Docker Desktop
- Make
- Node.js and npm (for MCP weather fallback)

### Required API Keys
Set these in `.env` (see `.env.example`):
- `OPENAI_API_KEY` (required)
- `TICKETMASTER_KEY` (required)
- `WEATHER_API_KEY` (optional - only for MCP fallback)

## Common Commands

### Development
```bash
make dev              # Build and run Docker container with hot reload
make restart          # Clean restart (stop + clean + dev)
make stop             # Stop running container
make clean            # Stop and remove container/image
make kill-port        # Kill process using port 7860
```

### Code Quality
```bash
make lint             # Run ruff linting and formatting
make fix              # Auto-fix issues and format code
make hooks            # Install pre-commit hooks locally
```

### Security
```bash
make security-scan    # Run gitleaks, pip-audit, and bandit
```

## Architecture

### Component Hierarchy
```
main.py
  └─ src/app.py (create_app)
       └─ ActivityAssistant
            ├─ ChatAssistant (OpenAI Agents SDK)
            │    ├─ Agent with function tools
            │    └─ WeatherMCPService
            ├─ TicketmasterAPI
            └─ GradioInterface (UI)
```

### Key Design Patterns

**Dual-Weather Service Strategy** (src/api/weather_mcp.py:14-28):
The app uses a cost-optimized fallback pattern:
1. Primary: Open-Meteo API (free, no API key) - supports current weather, forecasts, and location search
2. Fallback: MCP server with WeatherAPI (current weather + air quality only, requires `WEATHER_API_KEY`)

This ensures weather data availability while minimizing costs.

**MCP Implementation** (src/api/weather_mcp.py):
The fallback uses inter-process communication between Python and Node.js:
- **Python Client**: Uses the `mcp` library (mcp>=1.3.2) to connect to the MCP server
- **Node.js Server**: Runs `@swonixs/weatherapi-mcp` npm package via `npx -y`
- **Communication**: stdio (standard input/output) using `StdioServerParameters`
- **Tool Exposed**: `get_weather` tool with `location` parameter (current weather + air quality only)
- **Scope**: MCP fallback only applies to current weather; forecasts and location search use Open-Meteo exclusively
- **Environment**: `WEATHER_API_KEY` is passed as environment variable to the MCP server process

**Agent-Based Chat** (src/assistant_agent.py):
Uses OpenAI Agents SDK with function tools for structured tool calling:
- `get_weather()` - Fetches weather using dual-service strategy
- `get_ticketmaster_events()` - Searches events by city/country/keywords

The agent streams responses using `Runner.run_streamed()` and filters events by type to show only user-facing text (src/assistant_agent.py:220-225).

**Async/Sync Bridge** (src/app.py:56-78):
The app handles Gradio's synchronous interface with async agents by creating event loops per thread. This pattern is critical for proper streaming behavior.

### Agent Configuration

**System Prompt** (src/constants.py:92-172):
The agent has strict rules for activity recommendations:
- Maximum 10 activities total
- Smart balancing of indoor/outdoor/events based on weather
- Date interpretation logic (e.g., "tomorrow", "next Monday", "this weekend")
- Never mention "Ticketmaster" in responses
- Single-shot responses (no multi-turn confirmations)

**Model Selection** (src/constants.py:19):
Defaults to `gpt-4o-mini` but can be overridden via `MODEL` environment variable.

### API Limitations

**Ticketmaster** (README.md:73-84):
Only works in these countries: US, CA, GB, AU, AE, NO, NZ. For other locations, the app provides weather-based suggestions without events.

**Weather Services**:
- Open-Meteo: Global coverage, 16-day forecast max, current weather, geocoding (primary source)
- MCP/WeatherAPI (@swonixs/weatherapi-mcp): Current weather with air quality data only (fallback for current weather)

## CI/CD

### GitHub Actions Workflows

**.github/workflows/code-quality.yml**:
Runs on push to `feature-**`, `dev`, `main` branches and PRs:
- Ruff linting and format checks
- Triggers only when Python files or dependencies change

**.github/workflows/deploy-aws.yml**:
Deploys to AWS App Runner via ECR (Elastic Container Registry).

**.github/workflows/security.yml**:
Security scanning pipeline.

### Pre-commit Hooks

The project uses extensive pre-commit hooks (`.pre-commit-config.yaml`):
- **pre-commit**: Ruff linting + formatting
- **commit-msg**: Commitizen format validation, 50-char limit for first line
- **pre-push**: Gitleaks secret scanning, remote branch sync check

Install locally: `make hooks`

## File Structure

```
src/
├── api/
│   ├── weather.py         # Open-Meteo client (free)
│   ├── weather_mcp.py     # MCP service with fallback logic
│   └── events.py          # Ticketmaster API client
├── ui/
│   ├── interface.py       # Gradio UI setup
│   └── static/style.css   # Custom CSS
├── app.py                 # Main application orchestration
├── assistant_agent.py     # OpenAI Agent with tools
├── constants.py           # Config, prompts, UI text
└── logger.py              # Logging configuration
```

## Testing & Quality

**No test suite currently exists** - the project relies on:
- Pre-commit hooks (ruff, commitizen, gitleaks)
- CI/CD quality checks
- Manual testing via live demo

## Docker Deployment

The app runs on port 7860 by default. The Dockerfile sets up the environment with nginx and includes watchfiles for hot reloading in development.

**MCP Server Setup**: The Docker environment must have Node.js and npm installed to run the `@swonixs/weatherapi-mcp` package via npx. The Python MCP client spawns the Node.js server process dynamically when needed, communicating via stdio.

## Important Notes

- Python 3.12+ is not supported - use 3.11.x
- The app uses `uv` for package management, not pip
- MCP weather fallback requires:
  - Node.js and npm installed in the environment
  - `WEATHER_API_KEY` set in environment variables
  - The `@swonixs/weatherapi-mcp` package will be fetched automatically via `npx -y`
- Agent streaming responses filter out tool call arguments to show only user-facing text
- Event searches default to today's date if not specified
- The UI uses a custom dark theme with hardcoded styling (src/ui/interface.py:48-76)
