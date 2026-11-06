# Local development

## Prerequisites

- Python 3.13 or later and `uv`.
- Docker with the Compose plugin and access to the Docker daemon.
- Available host ports `5432`, `6379`, and `8000`.
- A repository checkout. Start the setup procedure from its root.

The Compose file is [docker-compose.yml](docker-compose.yml). It starts local
PostgreSQL 16 and Redis 7. It does not start FastAPI or a frontend.
The `smolink` database credentials are for local development only.

## Setup

1. If `backend/.env` does not exist, copy the configuration template:

   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` for your local environment.

   Replace the JWT, token-hash, and IP-hash placeholders with distinct random
   secrets. Keep this file uncommitted. Preserve an existing configuration.
   All `Settings` fields without defaults are required, including email and
   Google fields. Google routes are still pending. Actual email delivery
   requires a Resend key and a verified sender domain. Email links target
   `APP_PUBLIC_URL`. The frontend pages for those links are still planned.

3. Start the database services:

   ```bash
   docker compose -f docs/docker-compose.yml up -d
   ```

4. Check the services:

   ```bash
   docker compose -f docs/docker-compose.yml ps
   ```

   Wait until PostgreSQL and Redis report healthy. These checks report local
   service availability. They do not establish API correctness.

5. Change to the backend directory:

   ```bash
   cd backend
   ```

6. Install the locked dependencies:

   ```bash
   uv sync --frozen
   ```

7. Apply the reviewed migrations to the configured local database:

   ```bash
   uv run alembic upgrade head
   ```

   This command changes the database schema. Check `DATABASE_URL` before
   execution. Use a development database whose contents you can replace.

8. Start the API:

   ```bash
   uv run fastapi dev app/main.py
   ```

   The development API serves `http://127.0.0.1:8000`. `GET /health` returns
   `200` with `{"status":"ok"}`. Open `/docs` for generated API documentation.
   The health endpoint does not check PostgreSQL or Redis.

Run backend commands from `backend/`. The settings loader resolves `.env`
relative to the working directory. As an alternative development server, use
`uv run uvicorn app.main:app --reload`. Do not use `--reload` for production.

## Tests

Select checks with the [README testing policy](../README.md#testing-policy).
API tests with real dependencies are the primary backend safety net.
Selective unit tests protect focused invariants. Browser E2E remains planned.

Database and Redis integration tests use the configured local services.
They can create and delete test rows, create tables, and clear fixed test
rate-limit keys. Use an isolated development database and Redis instance.
Some API tests commit rows that remain after the case. Fixed limiter keys
also require cleanup. See the [walkthrough limits](codebase-walkthrough.md#tests-and-verification-limits).
Email tests replace the external sender or HTTP client.

1. Run the relevant test module for the changed behavior. This health example checks only `/health`:

   ```bash
   uv run pytest tests/test_health.py -q -s
   ```

2. If the change affects shared behavior, run the full suite:

   ```bash
   uv run pytest -q -s
   ```

3. Record the command, result, and date in the build checklist after successful verification.

`-s` avoids the output-capture cleanup issue recorded for this development
environment. Historical results remain in the
[checklist](backend-build-checklist.md#progress-log). They are not a promise
that the current working tree passes.

## New migrations

Prerequisites: a reviewed model change, a local database at the previous
migration head, and a correct `DATABASE_URL`. An applied migration is history.
Create a new revision instead of editing an applied revision.

1. Generate a revision:

   ```bash
   uv run alembic revision --autogenerate -m "describe change"
   ```

2. Inspect the generated `upgrade()` and `downgrade()` operations.

   Identify data deletion, dropped columns, changed constraints, and missing
   operations. Autogeneration does not establish migration correctness.

3. Apply the reviewed revision to the local database:

   ```bash
   uv run alembic upgrade head
   ```

4. Check the recorded revision:

   ```bash
   uv run alembic current
   ```

5. Run the relevant constraint and API tests.

For release validation, also test the migration chain against a separate
empty development database. No database-reset command is prescribed here.

## Troubleshooting

| Symptom | Check and expected result |
|---|---|
| Compose cannot find a configuration | Run from the repository root with `-f docs/docker-compose.yml`. |
| Docker reports permission denied | Check local Docker-daemon access. This is a host configuration issue. |
| Required settings are missing | Run from `backend/`. Compare variable names with `.env.example` and `Settings`. |
| PostgreSQL cannot connect | Check Compose health and the host/port in `DATABASE_URL`. The template uses `localhost:5432`. |
| Redis cannot connect | From the root, run `docker compose -f docs/docker-compose.yml exec redis redis-cli ping`. Expect `PONG`. |
| Protected writes return `503` | Check Redis connectivity. The rate limiter fails closed. |
| A write returns `429` | Wait for the `Retry-After` interval before another request. |
| An async test reports a different or closed event loop | Check that the fixture creates and closes each async client in the same event loop. |
| A test import fails | Check whether the module and imported symbol exist in the current working tree. |

Read the traceback before changing code. Inspect dependency failures through
a debugger or server logs. Preserve the limiter's `503` handling when
investigating Redis errors.
