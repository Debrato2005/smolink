# Smolink — Engineering Context

This file is the source of truth for anyone (human or AI) making changes to Smolink. It exists so decisions don't get re-litigated or silently reversed. If you're an AI assistant working on this repo, read this before touching code.

## Project Vision

Smolink is a URL shortener built to demonstrate real backend engineering judgment, not maximum technology usage. The measure of success is "did I make the right call for the constraints," not "how many distributed-systems buzzwords does this repo contain."

## Core Principles

1. Every technology in the stack must solve a problem that actually exists at this project's scale — not a problem it might have at Google scale.
2. Architecture evolves in phases (see README roadmap). Don't jump ahead — e.g. don't add Kafka before there's a real async workload for it to carry.
3. Prefer boring, well-understood tools over novel ones, except where the novelty *is* the point (e.g. exploring Rust for a specific hot path is a legitimate learning goal — exploring five different queue technologies is not).
4. Every architectural decision recorded here has a stated reason. If you want to change one, update the reason, don't just delete it.

## Non-Goals

- This is **not** attempting full microservices. Services are extracted only when a boundary is genuinely async/decoupled (see Architecture Decisions below).
- This is **not** optimizing for hypothetical scale (millions of req/s). It's optimizing for demonstrating that the author understands the tradeoffs involved in getting there.
- Live alias-availability checking, custom domains, team workspaces — all explicitly deferred, not forgotten.

## Architecture Decisions

### 1. Modular monolith, not microservices (current)
**Reasoning:** The redirect path (hot, read-heavy, latency-sensitive) and the creation path (cold, write-light) have different traffic profiles, but a cache layer in front of one service captures most of that benefit without network-separated services. Splitting `shortener`/`redirect` into separate services would add a network hop to a codepath that should be sub-millisecond — a regression, not an upgrade.

**What's a real extraction candidate:** analytics/click-tracking. It is naturally async and decoupled. The first backend release records click events synchronously; if measurement shows that this harms redirect latency, the redirect handler can publish events to a queue and a separate consumer can aggregate them.

**Module boundaries inside the monolith** (each owns its own data access; no cross-module DB queries):
- `shortener` — encode/decode, collision handling, custom aliases
- `redirect` — cache-first lookup, fallback to DB, publishes click events
- `analytics` — records and reports click events; it becomes an asynchronous consumer only when measurement justifies extraction
- `auth` — JWT issuance/verification, optional-auth middleware

### 2. Auth is optional
Guests can create short URLs without an account. Registered users get a dashboard, analytics, and management. This means most creation-path logic must work correctly with `user_id = null`.

### 3. PostgreSQL is the source of truth; Redis is cache-only for durable data
Never write logic that treats Redis as authoritative for URL or user data. If Redis is unavailable, redirects must degrade to hitting Postgres directly (cache-aside, not cache-only). Redis also holds ephemeral rate-limit counters; those counters are enforcement data, not durable application data.

### 4. Short code generation: Snowflake ID + Base62 encoding
Chosen over random generation for collision-free uniqueness without a "check and retry" loop at insert time.

### 5. No dedicated alias-availability endpoint
`POST /api/v1/urls` returning `409 Conflict` is the only mechanism in v1. Reasoning: an availability-check endpoint's only purpose is UX (live validation while typing), and overloading the create endpoint with a `check_only` flag violates single-responsibility. If live validation is added later, it should be a genuinely separate `GET /api/v1/aliases/{alias}/availability` endpoint with frontend debouncing — not a repurposed create call.

### 6. Route identifier convention
- `short_code` → public/unauthenticated routes (`/{short_code}`, `/api/v1/urls/{short_code}/qr`)
- `id` → owned-resource CRUD under `/api/v1/me/urls/{id}`

Do not unify these "for simplicity" — they serve different access-control contexts (public lookup vs. ownership-checked mutation).

### 7. Health checks: `/health` only until orchestration exists
`/live` and `/ready` are meaningful once there's an orchestrator (Kubernetes, Docker Swarm) deciding whether to restart or route traffic to an instance. Adding them before Phase 11 (multiple instances / load balancing) is premature.

### 8. Strict Redis-backed rate limiting
Rate limiting uses atomic fixed-window Redis counters. Registration and login share a limit of 5 attempts per IP per minute; guest URL creation is limited to 10 requests per IP per minute; authenticated URL creation is limited to 30 requests per user per minute. Redirects and `/health` are not rate-limited. Exceeded limits return `429 Too Many Requests` with `Retry-After`. If Redis is unavailable, redirect caching falls back to Postgres, while rate-limited write routes fail closed with `503` so abuse protection is not silently disabled.

## Current Backend Roadmap

1. **Foundation** — FastAPI configuration, Docker Compose, PostgreSQL, Redis, and `/health`.
2. **Data layer** — async SQLAlchemy, Alembic, and the `users`, `urls`, and `click_events` tables.
3. **URL utilities** — Snowflake IDs, Base62 encoding, and custom-alias validation.
4. **Rate limiting** — strict Redis-backed limits for authentication and URL creation.
5. **Auth and creation** — JWT authentication plus optional-auth URL creation for guests and users.
6. **Core URL features** — owner management, cache-aside redirects, QR generation, and full analytics.
7. **Verification and next phases** — tests and documentation, followed by frontend and deployment work.

## API Standards

- Errors use `{ "error": "<short code>", "message": "<human readable>" }`.
- Conflicts → `409`. Validation failures → `422` (FastAPI/Pydantic default). Not found → `404`. Auth required → `401`. Forbidden (wrong owner) → `403`.
- Rate limits → `429` with `Retry-After`; an unavailable rate limiter on protected writes → `503`.
- Pagination via `?page=&limit=`; search/filter/sort are additive query params, never separate endpoints.
- The initial API uses `/api/v1/`; no breaking changes to existing response shapes are allowed without a new version.

## Canonical Backend Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Application health check |
| `POST` | `/api/v1/auth/register` | Register a user |
| `POST` | `/api/v1/auth/login` | Authenticate and receive a JWT |
| `POST` | `/api/v1/urls` | Create a URL as a guest or authenticated user |
| `GET` | `/api/v1/me/urls` | List the authenticated user's URLs |
| `PATCH` | `/api/v1/me/urls/{id}` | Update an owned URL |
| `DELETE` | `/api/v1/me/urls/{id}` | Delete an owned URL |
| `GET` | `/api/v1/me/urls/{id}/analytics` | Retrieve full analytics for an owned URL |
| `GET` | `/api/v1/urls/{short_code}/qr` | Generate a QR PNG for a public code |
| `GET` | `/{short_code}` | Redirect to the destination URL |

## Proposed Project Structure

*(Proposed — adjust as implementation lands; not yet locked in.)*

```
smolink/
├── app/
│   ├── main.py
│   ├── core/          # config, security, dependencies
│   ├── shortener/      # module: encode/decode, alias logic
│   ├── redirect/       # module: cache-first lookup
│   ├── analytics/      # module: click recording and reporting
│   ├── auth/           # module: JWT, optional-auth
│   ├── models/         # SQLAlchemy models
│   ├── schemas/         # Pydantic request/response models
│   └── db/             # session, migrations (Alembic)
├── tests/
├── docker-compose.yml
└── alembic/
```

## Data Model Overview

*(Needs clarification — no schema has been finalized yet. Sketch below for reference only.)*

- **User**: id, email, password_hash, created_at
- **Url**: id, short_code, destination, owner_id (nullable), expires_at, total_clicks, last_clicked_at, created_at. `short_code` stores either the generated Base62 code or a custom alias; there is no separate `custom_alias` field.
- **ClickEvent**: id, url_id, timestamp, browser, os, device_type, referrer, ip_hash. Store a keyed IP hash only; never store a raw IP address.

## Invariants — Do Not Break

- Redirect latency must not depend on a network call to another service; measure synchronous analytics capture before introducing a queue or worker.
- Guest-created URLs must remain fully functional with no `owner_id`.
- No cross-module direct DB access — go through the owning module's interface.
- Redis is never the only place a piece of data exists.
- Rate-limit counters are ephemeral Redis enforcement data; durable application data remains in Postgres.

## Future Expansion Ideas

Password-protected links, scheduled activation, bulk shortening, custom domains, team workspaces, tags/collections, public API with API keys, `/live` + `/ready` once orchestration is introduced.

## Open Questions

- Exact DB schema (fields, indexes) — not yet finalized.
- Deployment target details beyond "Oracle Cloud VM" (single instance vs. planned multi-instance timeline).
