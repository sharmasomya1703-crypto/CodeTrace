# Contributing

Thanks for improving CodeTrace!

## Setup

```bash
# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -e ".[dev]"
pytest

# Frontend
cd frontend
npm install
npm run build
```

Or with Docker:

```bash
docker compose up --build
```

## Guidelines

- Keep algorithms pure and event-driven
- Prefer small, focused PRs
- Add tests for new algorithms, problems, and runner edge cases
- Do not commit secrets; use `.env.example` as the template
- Do not claim the subprocess runner is a full sandbox
- Match existing style: type hints, Pydantic models, concise React components

## Checks before PR

```bash
cd backend && ruff check . && pytest
cd frontend && npm run lint && npm run typecheck && npm run build
```

GitHub Actions runs lint, typecheck, tests, and builds on push/PR.

## Code of conduct

Be respectful. This project is for students learning algorithms — clarity beats cleverness.
