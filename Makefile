# ============================================================
# CodeWhisper PR - Makefile
# ============================================================

.PHONY: help setup dev build test lint clean docker-up docker-down
.PHONY: backend-setup frontend-setup db-migrate db-seed format

GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help:
	@echo "${GREEN}CodeWhisper PR - Commands${NC}"
	@echo ""
	@echo "${YELLOW}Setup:${NC}"
	@echo "  setup              Install all dependencies"
	@echo "  backend-setup      Setup backend with Poetry"
	@echo "  frontend-setup     Setup frontend with Yarn"
	@echo ""
	@echo "${YELLOW}Development:${NC}"
	@echo "  dev                Start development servers"
	@echo "  docker-up          Start Docker containers"
	@echo "  docker-down        Stop Docker containers"
	@echo ""
	@echo "${YELLOW}Database:${NC}"
	@echo "  db-migrate         Run database migrations"
	@echo "  db-seed            Seed database"
	@echo ""
	@echo "${YELLOW}Quality:${NC}"
	@echo "  test               Run all tests"
	@echo "  lint               Run linters"
	@echo "  format             Format code"
	@echo ""
	@echo "${YELLOW}Build:${NC}"
	@echo "  build              Build all apps"
	@echo "  clean              Clean build artifacts"

setup: backend-setup frontend-setup
	@echo "${GREEN}✓ Setup complete!${NC}"

backend-setup:
	@echo "${YELLOW}Setting up backend...${NC}"
	cd apps/backend && poetry install
	cd apps/backend && poetry run pre-commit install
	@echo "${GREEN}✓ Backend setup complete${NC}"

frontend-setup:
	@echo "${YELLOW}Setting up frontend...${NC}"
	cd apps/frontend && yarn install
	@echo "${GREEN}✓ Frontend setup complete${NC}"

dev:
	@echo "${YELLOW}Starting development servers...${NC}"
	@echo "${GREEN}✓ Frontend: http://localhost:3001${NC}"
	@echo "${GREEN}✓ Backend API: http://localhost:8000${NC}"
	@echo "${GREEN}✓ API Docs: http://localhost:8000/api/docs${NC}"
	yarn dev

docker-up:
	@echo "${YELLOW}Starting Docker containers...${NC}"
	docker-compose up -d
	@echo "${GREEN}✓ All containers started${NC}"

docker-down:
	@echo "${YELLOW}Stopping Docker containers...${NC}"
	docker-compose down
	@echo "${GREEN}✓ All containers stopped${NC}"

db-migrate:
	@echo "${YELLOW}Running database migrations...${NC}"
	cd apps/backend && poetry run alembic upgrade head
	@echo "${GREEN}✓ Migrations complete${NC}"

db-seed:
	@echo "${YELLOW}Seeding database...${NC}"
	cd apps/backend && poetry run python scripts/seed_db.py
	@echo "${GREEN}✓ Database seeded${NC}"

test:
	@echo "${YELLOW}Running tests...${NC}"
	yarn test
	@echo "${GREEN}✓ Tests complete${NC}"

lint:
	@echo "${YELLOW}Running linters...${NC}"
	yarn lint
	cd apps/backend && poetry run ruff check .
	@echo "${GREEN}✓ Linting complete${NC}"

format:
	@echo "${YELLOW}Formatting code...${NC}"
	cd apps/backend && poetry run black .
	cd apps/backend && poetry run isort .
	cd apps/frontend && yarn format
	@echo "${GREEN}✓ Formatting complete${NC}"

build:
	@echo "${YELLOW}Building all apps...${NC}"
	yarn build
	@echo "${GREEN}✓ Build complete${NC}"

clean:
	@echo "${YELLOW}Cleaning build artifacts...${NC}"
	yarn clean
	cd apps/backend && rm -rf .pytest_cache .mypy_cache .ruff_cache
	cd apps/frontend && rm -rf .next node_modules
	@echo "${GREEN}✓ Cleanup complete${NC}"
