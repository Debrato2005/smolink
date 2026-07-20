# Smolink Backend Build Checklist

This is the living execution tracker for the backend-first release. Update a checkbox only after its listed verification command passes. Keep a short note under **Progress log** whenever a task is completed, blocked, or deliberately deferred.

## Goal and fixed decisions

- Build one FastAPI modular monolith under `/api/v1`.
- PostgreSQL is authoritative for durable data.
- Redis is cache-aside for redirects and holds ephemeral rate-limit counters.
- Redirect-cache failure falls back to Postgres; a rate-limiter failure on protected writes returns `503`.
- Guests can create URLs; authenticated users manage URLs and view analytics.
- IDs use Snowflake generation plus Base62 encoding; custom aliases share the `short_code` field.
- First release analytics are synchronous and measured before Kafka or a worker is considered.

## Planned full-product follow-on

The backend release is not the end of Smolink. After its API contracts are verified, build and ship the full product using this direction:

- **Frontend:** React with TypeScript, consuming the documented `/api/v1` endpoints only.
- **Component system:** shadcn/ui for accessible application primitives and React Bits for expressive interface components. Keep shared primitives centralized; do not copy component code independently into each page.
- **Visual direction:** Paper Shaders for carefully bounded visual effects, GSAP for intentional motion, and Lenis for smooth scrolling where it improves the page experience.
- **Design process:** use Figma for polished screen and component decisions; use Excalidraw for architecture, data-flow, and interaction sketches. Use Dribbble as visual inspiration, not as a source to copy.
- **Production:** complete proxy-aware client-IP handling before enabling IP-based production limits, then add NGINX, HTTPS, CI/CD, cloud deployment, metrics, monitoring, and alerting.
- **Accessibility and performance:** honor `prefers-reduced-motion`, preserve keyboard navigation and contrast, do not make shader/animation loading block URL creation or dashboard content, and measure Core Web Vitals before retaining expensive effects.

## Working rules

1. Follow red → green: write a focused failing test, run it, add the minimum code, then rerun the relevant and full suite.
2. Do not commit `.env`, real secrets, database volumes, or local generated assets.
3. Make one focused commit after each completed milestone.
4. Do not mark a task complete because the code looks right. Mark it only after the stated verification succeeds.
5. Use `uv run pytest -q -s` in this environment. `-s` avoids an external pytest output-capture cleanup issue; application tests still run normally.

## Current verified state

- **Last verified:** 2026-07-18
- **Command:** `cd backend && uv run pytest -q -s`
- **Result:** `2 passed`; one third-party FastAPI/Starlette test-client deprecation warning.
- **Current files changed locally:** application entry point, typed settings, environment example, tests, dependency lockfiles, and local Compose infrastructure. These are not committed yet.

## Day 1 — Foundation, persistence, and URL creation

### A. Foundation cleanup — 20 minutes

- [x] Add FastAPI test dependencies: `pytest` and `httpx`.
- [x] Add `GET /health` returning `200` and `{"status": "ok"}`.
- [x] Add a health API test.
- [x] Add `pydantic-settings`.
- [x] Add typed environment settings for database URL, Redis URL, JWT secret, IP-hash secret, public base URL, and cache TTL.
- [x] Add a settings test using isolated environment variables.
- [x] Add `backend/.env.example` with placeholders only.
- [x] Confirm the repository `.gitignore` covers `backend/.env`, `.pytest_cache/`, `__pycache__/`, and local database-volume paths; no redundant backend-specific ignore file is needed.
- [ ] Remove the unused `BaseModel` import and tutorial-only `GET /` route from `app/main.py`; keep `create_app()` and `/health`.
- [ ] Run: `uv run pytest -q -s`.
- [ ] Commit: `chore: establish application configuration`.

### B. Local infrastructure — 60 minutes

- [x] Add runtime dependencies: async SQLAlchemy, `asyncpg`, Alembic, async Redis client, Argon2 password hashing, JWT library, QR library, and user-agent parser.
- [x] Create `docker-compose.yml` with named-volume PostgreSQL and Redis services.
- [x] Use non-secret development credentials only in Docker Compose; put application connection strings in `.env`.
- [x] Add Postgres and Redis health checks to Compose.
- [x] Start services: `docker compose up -d`.
- [x] Verify: `docker compose ps` shows both services healthy.
- [x] Verify Postgres connectivity with the application connection string and Redis with `redis-cli ping` from the Redis container.
- [ ] Commit: `chore: add local postgres and redis services`.

### C. Database foundation — 90 minutes

- [x] Create `app/db/session.py` with one async SQLAlchemy engine, one async session factory, and a FastAPI dependency that yields a session and closes it afterward.
- [x] Create `app/db/base.py` as the shared SQLAlchemy declarative base and model-import location for Alembic.
- [x] Initialize Alembic under `backend/alembic/` and configure it to use the application database URL.
- [x] Write a database-session smoke test that opens a connection and runs `SELECT 1` against the Compose Postgres service.
- [x] Run the smoke test before implementation and confirm it fails because the session dependency does not exist.
- [x] Implement the smallest engine/session setup to pass it.
- [x] Run: `uv run pytest tests/test_db_session.py -q -s`.
- [ ] Commit: `feat: add async database session support`.

### D. Initial data model and migration — 120 minutes

- [ ] Create `User`: Snowflake `BIGINT` id, unique indexed email, Argon2 password hash, created timestamp.
- [ ] Create `Url`: Snowflake `BIGINT` id, unique indexed `short_code`, destination, nullable owner id, nullable expiry, `total_clicks` default `0`, nullable `last_clicked_at`, timestamps.
- [ ] Create `ClickEvent`: id, URL foreign key, click timestamp, browser, OS, device type, referrer, keyed IP hash.
- [ ] Add indexes for `urls.short_code`, URL ownership/listing, and `click_events.url_id + clicked_at`.
- [ ] Generate the initial Alembic migration; inspect it before applying.
- [ ] Apply the migration to the local Postgres service.
- [ ] Write integration tests proving uniqueness and foreign-key constraints work.
- [ ] Run: `uv run pytest tests/test_models.py -q -s` and `alembic upgrade head`.
- [ ] Commit: `feat: add initial url shortener schema`.

### E. Short-code utilities — 90 minutes

- [ ] Create tests for Base62 known values, zero handling, and invalid negative input.
- [ ] Implement Base62 encoding as a pure utility with no database or FastAPI imports.
- [ ] Create tests for Snowflake IDs: integer type, uniqueness across repeated calls, and creation-order sorting.
- [ ] Implement one configurable Snowflake generator; document machine-id configuration before multi-instance use.
- [ ] Create tests for aliases: allowed characters, 3–64 length boundaries, reserved words, and case-normalization rule.
- [ ] Implement alias validation. Use `short_code` for both generated codes and custom aliases; do not add `custom_alias` to the database.
- [ ] Run: `uv run pytest tests/test_short_codes.py -q -s`.
- [ ] Commit: `feat: add short code generation and alias validation`.

### F. URL creation vertical slice — 150 minutes

- [ ] Define request/response schemas for `POST /api/v1/urls`: destination, optional alias, optional expiry, and returned id/code/public URL/timestamps.
- [ ] Create shortener repository functions only for insert and lookup-by-code.
- [ ] Create shortener service rules: valid destination, future expiry, custom alias uniqueness, generated code path, and nullable owner id.
- [ ] Add domain exceptions and map alias conflicts to `{ "error": "alias_taken", "message": "..." }` with `409`.
- [ ] Write endpoint tests first: guest creation returns `201`, invalid body returns `422`, duplicate alias returns `409`.
- [ ] Register `POST /api/v1/urls` in the versioned router.
- [ ] Run: `uv run pytest tests/test_url_creation.py -q -s`.
- [ ] Commit: `feat: create guest short URLs`.

## Day 2 — Security, Redis behavior, and complete URL experience

### G. Rate-limit infrastructure — 90 minutes

- [ ] Write Redis tests for atomic increment, first-write expiry, separate keys, and over-limit behavior.
- [ ] Implement a Lua-backed fixed-window counter so increment and initial expiry are atomic.
- [ ] Define key formats: `rate:auth:{ip}`, `rate:create:guest:{ip}`, and `rate:create:user:{user_id}`.
- [ ] Add a common limiter dependency that returns `429` plus `Retry-After` when over limit.
- [ ] Add a Redis-failure test showing rate-limited writes return the documented `503` envelope.
- [ ] Do not apply this limiter to `/health` or `GET /{short_code}`.
- [ ] Commit: `feat: add strict redis rate limiting`.

### H. Authentication — 120 minutes

- [ ] Write tests for registration, duplicate email, login success, invalid password, missing token, and malformed token.
- [ ] Add Argon2 hashing and JWT issue/verify utilities.
- [ ] Add `POST /api/v1/auth/register` and `POST /api/v1/auth/login`.
- [ ] Apply the shared 5-attempts-per-IP-per-minute limiter to both routes.
- [ ] Implement `get_current_user()` and `get_optional_current_user()` dependencies.
- [ ] Update URL creation to attach the optional authenticated user id and choose the correct guest/user creation limit.
- [ ] Run: `uv run pytest tests/test_auth.py -q -s`.
- [ ] Commit: `feat: add optional JWT authentication`.

### I. Owned URL management — 90 minutes

- [ ] Write tests for list pagination, search, unauthenticated access, wrong owner, update, and delete.
- [ ] Add `GET /api/v1/me/urls?page=&limit=&search=&sort=`.
- [ ] Add `PATCH /api/v1/me/urls/{id}` for destination and expiry only.
- [ ] Add `DELETE /api/v1/me/urls/{id}` returning `204`.
- [ ] Require ownership and return `401`, `403`, or `404` correctly.
- [ ] Commit: `feat: add owned URL management`.

### J. Redirect cache-aside — 120 minutes

- [ ] Write tests for cache hit, cache miss, expired link, unknown link, cache invalidation, and Redis cache outage.
- [ ] Add `GET /{short_code}` after all `/api/v1` routes.
- [ ] Cache `{url_id, destination, expires_at}` by short code with a TTL that never exceeds link expiry.
- [ ] On cache failure, log and query Postgres; return `302` when the URL exists.
- [ ] Return `404` for unknown links and `410` for existing expired links.
- [ ] Invalidate cache after database-first update or delete.
- [ ] Commit: `feat: add cache-aside URL redirects`.

### K. QR and analytics — 150 minutes

- [ ] Write a QR endpoint test expecting `image/png`, correct public URL content, `404`, and `410` cases.
- [ ] Add `GET /api/v1/urls/{short_code}/qr`; generate PNG on demand only.
- [ ] Write click-event tests for browser/OS/device/referrer extraction, keyed IP hash, aggregate counter, and last-clicked timestamp.
- [ ] Record a synchronous click event after resolving a successful redirect.
- [ ] Write analytics authorization and date-range tests.
- [ ] Add `GET /api/v1/me/urls/{id}/analytics?from=&to=&timezone=` with totals, daily series, and browser/OS/device/referrer breakdowns.
- [ ] Record redirect latency during analytics tests or a local benchmark; defer Kafka unless measurement shows a real problem.
- [ ] Commit: `feat: add QR generation and URL analytics`.

### L. Release verification and documentation — 60 minutes

- [ ] Run all tests: `uv run pytest -q -s`.
- [ ] Run migrations from an empty local database: `alembic upgrade head`.
- [ ] Manually test: create guest URL, redirect, register/login, create owned URL, exhaust a limit, update/delete owned URL, QR response, analytics report.
- [ ] Confirm all documented endpoint paths and status codes match implementation.
- [ ] Update `README.md`, `ENGINEERING_PLAYBOOK.md`, and this checklist with final verified status.
- [ ] Commit: `docs: record backend implementation status`.

## Full-product phases after the two-day backend release

### M. Product design and frontend foundation

- [ ] Create Figma frames for Home, Login, Register, Dashboard, URL detail/analytics, and empty/error states.
- [ ] Create an Excalidraw diagram for browser → NGINX → FastAPI → Redis/Postgres and the authentication/redirect flows.
- [ ] Bootstrap a React + TypeScript frontend with environment-based API base URL configuration.
- [ ] Add routing, typed API client modules, shared error parsing, and JWT attachment only for protected requests.
- [ ] Install and configure shadcn/ui; define shared button, form, dialog, toast, table, skeleton, and empty-state primitives.
- [ ] Add React Bits components only where they support the selected interaction or visual hierarchy.
- [ ] Add a motion policy using GSAP and Lenis; respect `prefers-reduced-motion` and provide non-animated fallbacks.
- [ ] Evaluate Paper Shaders on target devices; lazy-load and disable effects that hurt initial render, battery use, or accessibility.

### N. Frontend feature delivery

- [ ] Build guest URL creation, validation feedback, copy-to-clipboard, generated-link result, and QR preview/download.
- [ ] Build registration and login flows with token-expiry handling.
- [ ] Build protected URL dashboard: pagination, search, sort, empty state, update, and delete confirmation.
- [ ] Build analytics page with date filters and charts for daily, browser, OS, device, and referrer breakdowns.
- [ ] Map API errors consistently: `409` alias conflict, `422` field errors, `429` with retry guidance, `401` login redirect, `403` access denied, and `503` retryable service message.
- [ ] Test responsive layouts, keyboard navigation, screen-reader labels, reduced-motion behavior, and mobile performance.

### O. Rate-limit management and production client identity

- [ ] Add owner/admin-facing rate-limit configuration or dashboard UI only after the backend exposes safe, authenticated configuration/reporting endpoints.
- [ ] Document trusted proxy boundaries and configure NGINX to supply forwarded client information.
- [ ] Update FastAPI client-IP extraction to trust forwarded headers only from configured proxies; never trust arbitrary client-supplied `X-Forwarded-For` headers.
- [ ] Add tests for direct, proxied, spoofed, and missing client-IP headers before enabling production IP rate limits.

### P. Deployment and observability

- [ ] Add production Docker images and Compose/host configuration for frontend, FastAPI, Postgres, Redis, and NGINX.
- [ ] Configure NGINX routing, TLS termination, compression, security headers, and static frontend delivery.
- [ ] Obtain and renew HTTPS certificates; test HTTP-to-HTTPS redirects.
- [ ] Add CI for formatting, tests, migration validation, build checks, and frontend accessibility/lint checks.
- [ ] Deploy to the selected cloud VM with backup, restore, secret-management, and rollback procedures documented.
- [ ] Add structured logs, request IDs, redirect latency, database timing, Redis hit ratio, rate-limit rejections, and error metrics.
- [ ] Add dashboards and alerts for uptime, error rate, redirect latency, database/Redis availability, TLS expiry, disk space, and backup failures.

### Q. Later backend scale work

- [ ] Kafka, analytics worker, and raw-event retention job only after metrics demonstrate that synchronous analytics affects redirect latency or throughput.

## Progress log

| Date | Completed work | Verification | Notes |
|---|---|---|---|
| 2026-07-18 | Health endpoint and typed settings | `uv run pytest -q -s` → 2 passed | Pytest needs `-s` in this environment because its capture cleanup is external to the application. |
| 2026-07-18 | Local Postgres and Redis services started | `docker compose ps` → both services healthy | Restored user access to the Docker socket by joining the local `docker` group; no application-code change was needed. |
| 2026-07-19 | Local service connectivity | Postgres `SELECT 1` → `1`; Redis `redis-cli ping` → `PONG` | Postgres check used the application's configured `DATABASE_URL` from `backend/.env`. |
| 2026-07-20 | Async database session dependency | `uv run pytest tests/test_db_session.py -q -s` → 1 passed | Test first failed with missing `session.get_session`, then passed after the minimal engine, session factory, and yielding dependency were added. |
| 2026-07-20 | Async Alembic environment | `uv run alembic current` connected using `PostgresqlImpl` | Alembic reads `DATABASE_URL` through application settings and uses `Base.metadata`; no revisions exist yet. |
