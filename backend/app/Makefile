.PHONY: help install init-db migrate upgrade downgrade run test clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

init-db: ## Initialize database tables
	python init_db.py

migrate: ## Create a new migration
	alembic revision --autogenerate -m "$(message)"

upgrade: ## Apply all pending migrations
	alembic upgrade head

downgrade: ## Downgrade to previous migration
	alembic downgrade -1

run: ## Run the development server
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests (placeholder)
	@echo "Tests not implemented yet"

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 