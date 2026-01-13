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

**Dual-Weather Service Strategy** (src/api/weather_mcp.py:14-23):
The app uses a cost-optimized fallback pattern:
1. Primary: Open-Meteo API (free, no API key)
2. Fallback: MCP server with WeatherAPI (premium features, requires `WEATHER_API_KEY`)

This ensures weather data availability while minimizing costs. The MCP server path is hardcoded to `/opt/weather-mcp-server` for Docker deployment.

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
- Open-Meteo: Global coverage, 16-day forecast max
- MCP/WeatherAPI: Premium features (air quality, alerts)

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

MCP server must be available at `/opt/weather-mcp-server` for fallback weather functionality.

## Important Notes

- Python 3.12+ is not supported - use 3.11.x
- The app uses `uv` for package management, not pip
- Weather fallback requires the MCP server to be properly configured with `WEATHER_API_KEY`
- Agent streaming responses filter out tool call arguments to show only user-facing text
- Event searches default to today's date if not specified
- The UI uses a custom dark theme with hardcoded styling (src/ui/interface.py:48-76)
