# Repository Guidelines

## Project structure and modules

Smolink is a backend-first URL shortener. The Python application is in
`backend/app/`:

- `api/`: versioned FastAPI routes and dependencies.
- `core/`: shared configuration and Redis support.
- `db/`: async engine, sessions, and declarative base.
- `schemas/`: Pydantic request/response contracts.
- `services/`: business rules and coordination.
- `repositories/`: SQL access.
- `models/`: SQLAlchemy URL, analytics, and authentication tables.

Add future tables to `models/` and import them for Alembic discovery.

Tests live in `backend/tests/` and follow the source feature they cover. Alembic
configuration is in `backend/alembic.ini`. Migrations live in `backend/alembic/`.
Use `README.md` for architecture decisions. Use
[backend-build-checklist.md](backend-build-checklist.md) for the current milestone.
Update [codebase-walkthrough.md](codebase-walkthrough.md) when behavior changes.

## Development commands

Use [development.md](development.md) for setup, test, migration, and
troubleshooting procedures. Run backend commands from `backend/`. From the
repository root, select `docs/docker-compose.yml` explicitly for Compose.
Never commit `.env` files, real secrets, or database volumes.

## Coding style and names

Use Python 3.13 or later, four-space indentation, and type annotations.
Use `snake_case` for modules, functions, fields, and variables.
Use `PascalCase` for classes and Pydantic/SQLAlchemy models. Keep routes thin.
Put validation in schemas, business rules in services, and SQL in repositories.
Preserve `/api/v1` and the project invariants in `README.md`.

## Testing rules

Use the [README testing policy](../README.md#testing-policy). For behavior
changes and bugs, establish a reproducible failing check at the highest
practical boundary that isolates the requirement. Then make the minimum
correct change and rerun focused and relevant broader suites.

Current backend confidence comes primarily from API tests and real
PostgreSQL/Redis integration. Keep useful selective unit tests. Browser E2E
remains planned. Do not require a unit test for every implementation step or
add superficial tests for counts or coverage. Use the
[Playbook selection questions](ENGINEERING_PLAYBOOK.md#test-quality-and-coding-agents).

Use `pytest`, naming files `test_<feature>.py` and functions
`test_<expected_behavior>()`. Use `-s` for the recorded output-capture cleanup
issue in this environment. Use meaningful document/configuration checks when
an automated behavior test adds no value.

## Skills and Graphify

Use the shared repository skills in `.agents/skills/` for FastAPI work, Python
testing, and codebase-relationship questions. When `graphify-out/graph.json`
exists, use Graphify to scope architecture questions before broad searching.
After source changes, run `graphify update .` from the repository root. See
[agent-tooling.md](agent-tooling.md) for commands, output handling, and how to
interpret inferred relationships.

## Commits and pull requests

Existing commits use concise imperative summaries, for example
`feat: add async database session support` or `docs: update architecture`.
Keep each commit focused on one milestone. PRs should state the motivation,
list verification commands and results, mention schema or environment changes,
and include screenshots only for frontend-visible work. Do not bundle deferred
Kafka, worker, or deployment work into a backend milestone.
