.PHONY: help install lint type test eval-offline run clean docker-build docker-run index smoke ui compose-up compose-down logs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

lint: ## Run linting
	ruff check src tests
	ruff format --check src tests

type: ## Run type checking
	mypy src

test: ## Run tests with coverage
	pytest

index: ## Index AI Act corpus
	python -m src.app.retrieval.index_ai_act --corpus-dir data/knowledge/ai_act --verbose

smoke: ## Run smoke tests
	@echo "Running smoke tests..."
	@echo "✅ Health check"
	curl -f http://localhost:8000/health || (echo "❌ Health check failed" && exit 1)
	@echo "✅ API endpoint test"
	curl -X POST http://localhost:8000/v1/answer \
		-H "Content-Type: application/json" \
		-d '{"question": "What are the prohibited AI practices?"}' || (echo "❌ API test failed" && exit 1)
	@echo "✅ All smoke tests passed"

eval-offline: ## Run offline evaluation
	python -m src.evals.eval_offline --use-compliance-pipeline

eval-offline-basic: ## Run basic offline evaluation
	python -m src.evals.eval_offline

run: ## Run the FastAPI server
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

ui: ## Run Streamlit UI
	streamlit run ui_app.py

ui-dev: ## Run Streamlit UI in development mode
	streamlit run ui_app.py --server.port 8501 --server.address 0.0.0.0

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

docker-build: ## Build Docker image
	docker build -t langsmith-demo .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env langsmith-demo

compose-up: ## Start all services with Docker Compose
	docker compose up -d

compose-down: ## Stop all services
	docker compose down

compose-build: ## Build all Docker images
	docker compose build

compose-logs: ## View logs from all services
	docker compose logs -f

logs: ## View logs from all services (alias for compose-logs)
	docker compose logs -f

compose-restart: ## Restart all services
	docker compose restart

compose-status: ## Show status of all services
	docker compose ps

compose-clean: ## Clean up Docker Compose resources
	docker compose down -v --remove-orphans
	docker system prune -f

observe-up: ## Start observability stack (Prometheus, Grafana, Loki)
	docker compose up -d prometheus grafana loki promtail

observe-down: ## Stop observability stack
	docker compose down prometheus grafana loki promtail

observe-status: ## Show observability stack status
	docker compose ps prometheus grafana loki promtail

observe-logs: ## View observability stack logs
	docker compose logs -f prometheus grafana loki promtail

observe-full: ## Start full stack with observability
	docker compose up -d

observe-grafana: ## Open Grafana in browser
	@echo "Opening Grafana at http://localhost:3000"
	@echo "Username: admin, Password: admin"
	@open http://localhost:3000 || xdg-open http://localhost:3000 || echo "Please open http://localhost:3000 in your browser"

observe-prometheus: ## Open Prometheus in browser
	@echo "Opening Prometheus at http://localhost:9090"
	@open http://localhost:9090 || xdg-open http://localhost:9090 || echo "Please open http://localhost:9090 in your browser"
