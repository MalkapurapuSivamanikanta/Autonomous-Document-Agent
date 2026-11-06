.PHONY: help install run test demo lint format docker-build docker-up

help:  ## Show this help
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-14s %s\n", $$1, $$2}'

install:  ## Install runtime and dev dependencies
	pip install -r requirements-dev.txt

run:  ## Start the API with auto-reload (http://127.0.0.1:8000/docs)
	uvicorn main:app --reload

test:  ## Run the test suite (no API key needed)
	pytest

demo:  ## Run both test inputs end to end (needs OPENAI_API_KEY)
	python run_demo.py

lint:  ## Lint and check formatting
	ruff check . && ruff format --check .

format:  ## Auto-fix lint issues and format the code
	ruff check --fix . && ruff format .

docker-build:  ## Build the Docker image
	docker build -t agent-docx .

docker-up:  ## Run the API in Docker (needs a .env file)
	docker compose up --build
