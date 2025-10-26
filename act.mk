# ACT Testing Commands
# All required environment variables are defined in the .env file
include .env
export

# Usage: make -f act.mk <target>


# =====================================
# 🚀 Continuous Delivery
# =====================================

test-aws:	## Test Hugging Face deployment
	act workflow_dispatch -W .github/workflows/deploy-aws.yml --input confirm_deployment=deploy --secret AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) --secret AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY)


# =====================================
# 📚 Documentation & Help
# =====================================

help: ## Show this help message
	@echo Available commands:
	@echo.
	@python -c "import re; lines=open('act.mk', encoding='utf-8').readlines(); targets=[re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$',l) for l in lines]; [print(f'  make {m.group(1):<20} {m.group(2)}') for m in targets if m]"

# =======================
# 🎯 PHONY Targets
# =======================

# Auto-generate PHONY targets (cross-platform)
.PHONY: $(shell python -c "import re; print(' '.join(re.findall(r'^([a-zA-Z_-]+):\s*.*?##', open('act.mk', encoding='utf-8').read(), re.MULTILINE)))")

# Test the PHONY generation
# test-phony:
# 	@echo "$(shell python -c "import re; print(' '.join(sorted(set(re.findall(r'^([a-zA-Z0-9_-]+):', open('act.mk', encoding='utf-8').read(), re.MULTILINE)))))")"
