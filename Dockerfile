FROM python:3.11-slim

# Install system dependencies: uv, Node.js, and npm
RUN pip install uv && \
    apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    node --version && npm --version && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (changes rarely)
COPY pyproject.toml uv.lock ./

# Put venv outside of /app so it won't be affected by volume mounts
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

# Install dependencies (this will now create venv at /opt/venv)
RUN uv sync --locked

# Copy all source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV DOCKER_ENV=1

# Disable UV cache entirely for production
ENV UV_NO_CACHE=1

ENV PORT=7860

# Expose the port
EXPOSE 7860

CMD ["uv", "run", "main.py"]
