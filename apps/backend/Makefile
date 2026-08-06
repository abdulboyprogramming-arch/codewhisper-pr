# ============================================================
# CodeWhisper PR - Backend Makefile
# ============================================================

.PHONY: help install dev test lint format clean migrate seed

GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:
	@echo "${GREEN}CodeWhisper PR Backend Commands${NC}"
	@echo "  install          Install dependencies"
	@echo "  dev              Run development server"
	@echo "  test             Run tests"
	@echo "  lint             Run linters"
	@echo "  format           Format code"
	@echo "  migrate          Run database migrations"
	@echo "  seed             Seed database"
	@echo "  clean            Clean build artifacts"

install:
	@echo "${YELLOW}Installing dependencies...${NC}"
	poetry install
	@echo "${GREEN}✓ Dependencies installed${NC}"

dev:
	@echo "${YELLOW}Starting development server...${NC}"
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "${YELLOW}Running tests...${NC}"
	poetry run pytest --timeout=30
	@echo "${GREEN}✓ Tests complete${NC}"

lint:
	@echo "${YELLOW}Running linters...${NC}"
	poetry run ruff check .
	poetry run mypy src --ignore-missing-imports || true
	@echo "${GREEN}✓ Linting complete${NC}"

format:
	@echo "${YELLOW}Formatting code...${NC}"
	poetry run black .
	poetry run isort .
	@echo "${GREEN}✓ Formatting complete${NC}"

migrate:
	@echo "${YELLOW}Running migrations...${NC}"
	poetry run alembic upgrade head
	@echo "${GREEN}✓ Migrations complete${NC}"

seed:
	@echo "${YELLOW}Seeding database...${NC}"
	poetry run python scripts/seed_db.py
	@echo "${GREEN}✓ Database seeded${NC}"

clean:
	@echo "${YELLOW}Cleaning build artifacts...${NC}"
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage
	@echo "${GREEN}✓ Cleanup complete${NC}"
