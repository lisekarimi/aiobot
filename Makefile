# =====================================
# 🌱 Project & Environment Configuration
# =====================================
# Read from pyproject.toml using grep (works on all platforms)
PROJECT_NAME = $(shell python3 -c "import re; print(re.search('name = \"(.*)\"', open('pyproject.toml').read()).group(1))")
VERSION = $(shell python3 -c "import re; print(re.search('version = \"(.*)\"', open('pyproject.toml').read()).group(1))")
-include .env
export

# Docker configuration
DOCKER_IMAGE = $(DOCKER_USERNAME)/$(PROJECT_NAME)
CONTAINER_NAME = $(PROJECT_NAME)-app
PORT ?= 7860

# =====================================
# 🐋 Docker Commands
# =====================================

build: ## Build Docker image with nginx
	docker build --no-cache -t $(DOCKER_IMAGE):$(VERSION) .

run: ## Run with hot reloading
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):$(PORT) \
		-v $(PWD):/app \
		--env-file .env \
		$(DOCKER_IMAGE):$(VERSION) \
		sh -c "pip install watchfiles && watchfiles 'uv run main.py' /app/src"
	@echo "🚀 Run this app at http://localhost:$(PORT)"

dev:  ## Run and build the docker container
	make build && make run

ls : ## List files inside the container
	docker run --rm $(DOCKER_IMAGE):$(VERSION) ls -la /app

stop: ## Stop the Docker container
	docker stop $(CONTAINER_NAME) || true

kill-port: ## Kill any process using port 7860
	@lsof -ti:$(PORT) 2>/dev/null | xargs -r kill -9 || true
	@fuser -k $(PORT)/tcp 2>/dev/null || true
	@echo "Port $(PORT) cleanup attempted"

clean: stop kill-port
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(DOCKER_IMAGE):$(VERSION) || true

restart: clean dev ## Restart Docker container (clean + run)


# =======================
# 🪝 Hooks
# =======================

hooks:	## Install pre-commit on local machine
	pip install pre-commit && pre-commit install && pre-commit install --hook-type commit-msg

# Pre-commit ensures code quality before commits.
# Installing globally lets you use it across all projects.
# Check if pre-commit command exists : pre-commit --version


# =====================================
# ✨ Code Quality
# =====================================

lint:	## Run code linting and formatting
	uvx ruff check .
	uvx ruff format .

fix:	## Fix code issues and format
	uvx ruff check --fix .
	uvx ruff format .


# =======================
# 🔍 Security Scanning
# =======================
security-scan:		## Run all security checks
	gitleaks detect --source . --verbose && uv run --with pip-audit pip-audit && uvx bandit -r src/


# =====================================
# 📚 Documentation & Help
# =====================================

help: ## Show this help message
	@echo "Available commands:"
	@echo ""
	@python3 -c "import re; lines=open('Makefile', encoding='utf-8').readlines(); targets=[re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$',l) for l in lines]; [print(f'  make {m.group(1):<20} {m.group(2)}') for m in targets if m]"


# =======================
# 🎯 PHONY Targets
# =======================

# Auto-generate PHONY targets (cross-platform)
.PHONY: $(shell python3 -c "import re; print(' '.join(re.findall(r'^([a-zA-Z_-]+):\s*.*?##', open('Makefile', encoding='utf-8').read(), re.MULTILINE)))")

# Test the PHONY generation
# test-phony:
# 	@echo "$(shell python3 -c "import re; print(' '.join(sorted(set(re.findall(r'^([a-zA-Z0-9_-]+):', open('Makefile', encoding='utf-8').read(), re.MULTILINE)))))")"
