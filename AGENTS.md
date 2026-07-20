# Repository Guidelines

## Project Structure & Module Organization

Smolink is a backend-first URL shortener. The Python application is in
`backend/app/`: `api/` contains versioned FastAPI routes, `core/` holds shared
configuration, `db/` owns the async engine and declarative base, `schemas/`
contains Pydantic request/response types, and `services/` and `repositories/`
separate business rules from SQL access. Put new SQLAlchemy table models in
`backend/app/models/` as the data-model milestone is completed.

Tests live in `backend/tests/` and follow the source feature they cover. Alembic
configuration and migrations live in `backend/alembic/`. Architecture decisions
are in `README.md`; use `docs/backend-build-checklist.md` to follow the current
milestone and update the learning notes in `docs/codebase-walkthrough.md` when
behaviour changes.

## Build, Test, and Development Commands

Run backend commands from `backend/`:

```bash
uv run fastapi dev app/main.py       # start the development API
uv run pytest -q -s                 # run the full test suite
uv run pytest tests/test_health.py -q -s  # run one focused test module
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head          # apply database migrations
```

From the repository root, `docker compose up -d` starts local PostgreSQL and
Redis; `docker compose ps` confirms their health. Copy `backend/.env.example`
to `backend/.env` for local configuration. Never commit `.env` files, real
secrets, or database volumes.

## Coding Style & Naming Conventions

Use Python 3.13, four-space indentation, type annotations, and `snake_case` for
modules, functions, fields, and variables. Use `PascalCase` for classes and
Pydantic/SQLAlchemy models. Keep routes thin: validation belongs in schemas,
business rules in services, and database queries in repositories. Preserve the
`/api/v1` API prefix and the project invariants in `README.md`.

## Testing Guidelines

Use `pytest`, naming files `test_<feature>.py` and functions
`test_<expected_behavior>()`. Write a focused failing test before implementing
a feature, then make the smallest change that passes. For database work, test
real constraints against the Compose PostgreSQL service. Use `-s` consistently
because this environment has a pytest output-capture cleanup issue.

## Commit & Pull Request Guidelines

Existing commits use concise imperative summaries, for example
`feat: add async database session support` or `docs: update architecture`.
Keep each commit focused on one milestone. PRs should state the motivation,
list verification commands and results, mention schema or environment changes,
and include screenshots only for frontend-visible work. Do not bundle deferred
Kafka, worker, or deployment work into a backend milestone.
