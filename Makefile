.PHONY: help install install-dev clean lint format type-check test test-cov run build docs clean-pyc clean-test clean-build

# ANSI color codes
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project variables
PYTHON := python3
UV := uv
PROJECT_NAME := holographic-chatbot
SRC_DIR := src/holographic_chatbot
TEST_DIR := tests

help: ## Show this help message
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║        Holographic Chatbot - Production Build System              ║$(NC)"
	@echo "$(BLUE)║        Author: Ruslan Magana (ruslanmv.com)                        ║$(NC)"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  1. make install      - Install dependencies using uv"
	@echo "  2. make test         - Run tests"
	@echo "  3. make run          - Run the application"
	@echo ""

install: ## Install production dependencies using uv
	@echo "$(GREEN)Installing production dependencies with uv...$(NC)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) pip install -e .; \
	else \
		echo "$(RED)Error: uv is not installed. Install it with: pip install uv$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Installation complete!$(NC)"

install-dev: ## Install development dependencies using uv
	@echo "$(GREEN)Installing development dependencies with uv...$(NC)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) pip install -e ".[dev,docs]"; \
	else \
		echo "$(RED)Error: uv is not installed. Install it with: pip install uv$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Development installation complete!$(NC)"

sync: ## Sync dependencies using uv
	@echo "$(GREEN)Syncing dependencies with uv...$(NC)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) pip sync; \
	else \
		echo "$(RED)Error: uv is not installed. Install it with: pip install uv$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Sync complete!$(NC)"

clean: clean-pyc clean-test clean-build ## Remove all build, test, coverage and Python artifacts

clean-pyc: ## Remove Python file artifacts
	@echo "$(YELLOW)Cleaning Python artifacts...$(NC)"
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	@echo "$(GREEN)✓ Python artifacts cleaned!$(NC)"

clean-test: ## Remove test and coverage artifacts
	@echo "$(YELLOW)Cleaning test artifacts...$(NC)"
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	@echo "$(GREEN)✓ Test artifacts cleaned!$(NC)"

clean-build: ## Remove build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	@echo "$(GREEN)✓ Build artifacts cleaned!$(NC)"

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m isort $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Code formatted!$(NC)"

lint: ## Lint code with ruff and flake8
	@echo "$(GREEN)Linting code...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR)
	@echo "$(GREEN)✓ Linting complete!$(NC)"

type-check: ## Type check code with mypy
	@echo "$(GREEN)Type checking code...$(NC)"
	$(PYTHON) -m mypy $(SRC_DIR)
	@echo "$(GREEN)✓ Type checking complete!$(NC)"

test: ## Run tests with pytest
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR) -v
	@echo "$(GREEN)✓ Tests complete!$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(PYTHON) -m pytest-watch $(TEST_DIR)

quality: format lint type-check test ## Run all quality checks (format, lint, type-check, test)
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║            All quality checks passed successfully! ✓               ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════════╝$(NC)"

run: ## Run the holographic chatbot application
	@echo "$(GREEN)Starting Holographic Chatbot...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Warning: .env file not found. Using .env.example as template...$(NC)"; \
		cp .env.example .env; \
		echo "$(YELLOW)Please edit .env file with your configuration before running.$(NC)"; \
		exit 1; \
	fi
	$(PYTHON) -m holographic_chatbot.main

build: clean ## Build distribution packages
	@echo "$(GREEN)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build complete! Packages in dist/$(NC)"

docs: ## Generate documentation with Sphinx
	@echo "$(GREEN)Generating documentation...$(NC)"
	cd docs && make html
	@echo "$(GREEN)✓ Documentation generated in docs/_build/html/index.html$(NC)"

install-system-deps: ## Install system dependencies (ffmpeg, espeak)
	@echo "$(GREEN)Installing system dependencies...$(NC)"
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && sudo apt-get install -y ffmpeg espeak-ng mpg123; \
	elif command -v brew >/dev/null 2>&1; then \
		brew install ffmpeg espeak-ng mpg123; \
	else \
		echo "$(RED)Error: Package manager not supported. Please install ffmpeg, espeak-ng, and mpg123 manually.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ System dependencies installed!$(NC)"

setup: install-system-deps install-dev ## Complete setup (system deps + dev installation)
	@echo "$(GREEN)╔════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║               Setup complete! Ready to develop.                    ║$(NC)"
	@echo "$(GREEN)╚════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure your API keys"
	@echo "  2. Run 'make test' to verify installation"
	@echo "  3. Run 'make run' to start the application"
	@echo ""

verify: ## Verify installation and dependencies
	@echo "$(GREEN)Verifying installation...$(NC)"
	@echo "$(BLUE)Python version:$(NC)"
	@$(PYTHON) --version
	@echo "$(BLUE)UV version:$(NC)"
	@$(UV) --version || echo "$(YELLOW)uv not installed$(NC)"
	@echo "$(BLUE)Installed packages:$(NC)"
	@$(PYTHON) -m pip list | grep -E "openai|pygltflib|pillow|requests|pygame|gtts"
	@echo "$(GREEN)✓ Verification complete!$(NC)"

.DEFAULT_GOAL := help
