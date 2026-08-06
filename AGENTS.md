# AGENTS.md - Development Guidance for CodeWhisper PR

## Project Structure

```
codewhisper-pr/
├── apps/
│   ├── backend/          # FastAPI Python backend
│   └── frontend/         # Next.js React frontend
├── packages/
│   ├── shared-types/     # Shared TypeScript types
│   ├── ui-components/    # Reusable React components
│   └── linting-config/   # Shared ESLint/Prettier config
├── infrastructure/
│   ├── terraform/        # IaC for AWS deployment
│   ├── kubernetes/       # K8s manifests
│   └── ansible/          # VM provisioning playbooks
```

## Commands

### Root
```bash
make dev            # Start all services with docker-compose
make build          # Build all images
make test           # Run all tests
make lint           # Run linters
make typecheck      # Run type checking
```

### Backend
```bash
cd apps/backend
make backend-install    # Poetry install
make backend-test       # pytest
make backend-lint       # flake8, mypy, black --check
make backend-run        # uvicorn
```

### Frontend
```bash
cd apps/frontend
yarn dev              # Next.js dev server
yarn test             # Jest
yarn lint             # ESLint
yarn type-check       # tsc --noEmit
```

## Conventions

- Use `C:/Users/...` path format with write tool (Windows path resolution)
- Backend: SQLAlchemy async engine, Pydantic v2 schemas, Loguru logging
- Frontend: React Query for data fetching, React Hook Form for forms
- TypeScript: camelCase for frontend, snake_case matches backend API
- All new Python files must have `# ============================================================` header comments
- All new TypeScript files must have header comment blocks

## Testing

- Backend: pytest with pytest-asyncio, use `tests/conftest.py` for fixtures
- Frontend: Jest + React Testing Library, test files in `src/` next to components
