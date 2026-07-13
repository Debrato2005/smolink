# Smolink Engineering Playbook

This is the teaching/reference document behind Smolink — it explains *why* backend systems are built the way they are, using Smolink as the running example. It is intentionally framework-agnostic where possible: the concepts apply to FastAPI, Django, Express, Spring Boot, or anything else.

**Relationship to the other two docs**, so nothing drifts out of sync:
- `README.md` — the canonical endpoint list and phase-by-phase implementation roadmap.
- `SMOLINK_CONTEXT.md` — the canonical list of fixed architectural decisions and invariants.
- **This file** — the conceptual "why," taught once, referenced everywhere else.

If something here ever conflicts with `SMOLINK_CONTEXT.md`, the context file wins — update this file to match, not the other way around.

## Table of Contents

- [Part 1 — Project Foundation](#part-1--project-foundation)
- [Part 2 — Backend Fundamentals](#part-2--backend-fundamentals)
- [Part 3 — Data Layer](#part-3--data-layer)
- [Part 4 — Business Logic](#part-4--business-logic)
- [Part 5 — API Layer](#part-5--api-layer)
- [Part 6 — Core Smolink Features](#part-6--core-smolink-features)
- [Part 7 — Performance & Scalability](#part-7--performance--scalability)
- [Part 8 — Frontend Architecture & Integration](#part-8--frontend-architecture--integration)
- [Part 9 — Quality Assurance & Testing](#part-9--quality-assurance--testing)
- [Part 10 — DevOps & Deployment](#part-10--devops--deployment)
- [Parts 11–14 — Planned (content pending)](#parts-1114--planned-content-pending)

---

# Part 1 — Project Foundation

*Before writing code: what are we building, and why? No implementation details in this section.*

## Vision

Smolink is a production-inspired URL shortener built from scratch, where the point isn't the working app — it's understanding the engineering behind it. Every technology introduced must solve a real problem at the point it's introduced; the repo's commit history should read as the evolution from a minimal REST API to a distributed-systems-informed backend.

## Objectives

**Primary:** backend engineering, REST API design, software architecture, database design, auth, caching, containerization, CI/CD, cloud deployment, monitoring, distributed systems, production practices.

**Secondary:** portfolio project, personal engineering reference, interview discussion piece, backend experimentation platform.

## Problem Statement & Target Users

Long URLs are hard to share; Smolink maps them to compact, unique identifiers.

| | Guests | Registered users |
|---|---|---|
| Shorten URLs | ✅ | ✅ |
| Custom alias, expiration, QR | ✅ | ✅ |
| Personal dashboard, history | ❌ | ✅ |
| Analytics | ❌ | ✅ |
| Search, pagination, API keys | ❌ | ✅ |

Auth *enhances* the experience; it is never required to shorten a URL.

## Functional Requirements

URL shortening · redirects · custom aliases · expiration · QR generation · optional auth · analytics (click count, browser, device, OS, timestamp, referrer, country-future) · dashboard.

## Non-Functional Requirements

- **Performance:** redirects must be fast; Redis exists specifically to keep the hot path off Postgres.
- **Scalability:** architecture should tolerate multiple app instances, load balancing, a shared cache, and eventual sharding — without requiring all of that on day one.
- **Reliability:** the system should degrade gracefully when a component fails (e.g. Redis down → fall back to Postgres, don't 500).
- **Maintainability:** one responsibility per component; business logic stays independent of infrastructure.
- **Security:** hashed passwords, JWT auth, validated input, parameterized queries/ORM (no raw string SQL).
- **Observability:** metrics exposed, errors logged, performance measurable.

## Engineering Principles

1. **Build incrementally** — never introduce a technology before it solves a real problem.
2. **Simplicity first** — the simplest architecture that solves *today's* problem; no premature optimization.
3. **Separation of concerns** — one responsibility per layer.
4. **Postgres is the source of truth** — Redis is cache, never authoritative.
5. **Stateless backend** — no in-memory session state, so instances stay horizontally scalable.
6. **Explicit design** — every endpoint, table, and module has a documented reason to exist.
7. **Production mindset** — even as a learning project, follow production-quality practice where practical.

## Technology Stack

Python · FastAPI · Pydantic · SQLAlchemy · Alembic · PostgreSQL · Redis · JWT · Kafka *(later)* · Docker · Docker Compose · NGINX · GitHub Actions · Prometheus · Grafana · Oracle Cloud (Ubuntu VM).

## High-Level Architecture

**v1:** `Internet → NGINX → FastAPI → PostgreSQL`

**Evolved:** `Internet → NGINX → Load Balancer → FastAPI instances → Redis → PostgreSQL → Kafka → Analytics Worker → Prometheus/Grafana`

The architecture is meant to grow *alongside* the project, not be built in full upfront.

## Project Constraints

These are treated as fixed unless consciously revisited — see `SMOLINK_CONTEXT.md` for the maintained, canonical version of this list:

- Guests can shorten URLs; auth is optional, never mandatory.
- PostgreSQL is the source of truth; Redis is cache-only.
- Snowflake ID + Base62 is the short-code strategy.
- Architecture starts as a modular monolith.
- Built incrementally — not feature-complete from day one.

---

# Part 2 — Backend Fundamentals

*Concepts that hold regardless of framework — FastAPI, Django, Express, Spring Boot, Go Fiber, Laravel all share these.*

## 0. How the Internet Works

Understanding what happens between a click and a response makes HTTP and REST intuitive rather than magic. When someone visits `https://smolink.com/abc123`:

1. **DNS resolution** — the browser resolves `smolink.com` to an IP address.
2. **TCP connection** — a three-way handshake establishes a reliable connection to that IP on port 443 (HTTPS) or 80 (HTTP).
3. **TLS handshake** — for HTTPS, client and server negotiate encryption before any data is exchanged.
4. **HTTP request sent** — the browser sends `GET /abc123` over the now-encrypted connection.
5. **Reverse proxy (NGINX)** — receives the request first, terminates TLS, and forwards it to the FastAPI process over the internal network.
6. **FastAPI handles it** — routes, validates, executes business logic, queries Redis/Postgres, returns a response.
7. **Response travels back** — FastAPI → NGINX → TCP → browser, which then follows the redirect.

Knowing this sequence is what makes concepts like "why do we need a reverse proxy," "why does HTTPS matter for login," and "what does a 502 actually mean" concrete instead of abstract.

## 9. HTTP Fundamentals

Every request has: **method, path, headers, body, query parameters.** Every response has: **status code, headers, body.**

| Method | Purpose | Modifies data? |
|---|---|---|
| GET | Retrieve | No |
| POST | Create | Yes |
| PUT | Replace entire resource | Yes |
| PATCH | Partial update — **preferred in Smolink** | Yes |
| DELETE | Remove | Yes |

**Status codes actually used in Smolink:**

| Code | Meaning | Example |
|---|---|---|
| 200 | OK | Successful GET |
| 201 | Created | Short URL created |
| 204 | No Content | Successful DELETE |
| 302 | Temporary redirect | Smolink's redirect (destinations can change) |
| 400 | Bad request | Invalid URL |
| 401 | Unauthenticated | Missing/invalid JWT |
| 403 | Forbidden | Authenticated but not the owner |
| 404 | Not found | Unknown short code |
| 409 | Conflict | Alias already taken |
| 410 | Gone | Link expired |
| 422 | Validation failed | FastAPI/Pydantic auto-response |
| 429 | Too many requests | Rate limit hit |
| 500 | Server error | Unexpected failure |

## 10. REST API Design

Think in **nouns, not verbs**: `/api/urls` not `/createURL`. Resources are acted on via HTTP methods, not baked into the path.

**Statelessness:** every request carries everything needed to process it (this is *why* Smolink uses JWT instead of server-side sessions — it lets multiple FastAPI instances work correctly without shared session state).

**Idempotency:** GET/PUT/DELETE are idempotent (repeating them leaves the same end state); POST is not (each call typically creates something new).

## 11. Request Lifecycle

```
React → POST /api/urls → NGINX → FastAPI Router
      → Pydantic validation → Service layer → Repository layer
      → PostgreSQL → back up through Repository → Service
      → API route → JSON response → React
```

Every request in Smolink follows this same pipeline — no shortcuts, no layer-skipping.

## 12. Folder Structure

Reconciled with the modular-monolith decision in `SMOLINK_CONTEXT.md`: each **domain module** owns its own layers internally, rather than one shared `services/`/`repositories/` folder spanning all domains. This keeps the "no cross-module DB access" invariant enforceable at the folder level.

```
app/
├── core/            # config, security, dependencies — shared, no business logic
├── db/              # engine, session, connection management — shared
├── shortener/
│   ├── router.py    # API layer
│   ├── schema.py    # Pydantic request/response models
│   ├── model.py     # SQLAlchemy model
│   ├── repository.py
│   └── service.py
├── redirect/
│   └── ...same shape
├── analytics/
│   └── ...same shape
└── auth/
    └── ...same shape
```

A module never imports another module's `repository.py` directly — if `redirect` needs something from `shortener`, it calls `shortener`'s service function, not its repository.

## 13. Layered Architecture (within each module)

```
Request → API layer → Service layer → Repository layer → Database
```

| Layer | Does | Never does |
|---|---|---|
| API | Receive HTTP, call service, return response | SQL, business rules |
| Service | Business rules, coordinates repositories | HTTP, SQL |
| Repository | DB operations only | HTTP, business decisions |
| Database | Storage, source of truth | — |

This separation is what makes testing tractable — you can unit-test a service function without spinning up HTTP or a real database.

## 14. Dependency Injection

FastAPI provides objects (DB session, current user, settings, logger) automatically via `Depends()` rather than each route manually constructing them. Less duplication, easier to swap real dependencies for test doubles.

## 15. Configuration Management

Never hardcode secrets. `.env` holds real values (never committed); `.env.example` is the template contributors copy. `pyproject.toml` holds dependencies/metadata, not secrets. Configuration loads once at startup and is reused — not re-read per request.

---

# Part 3 — Data Layer

*What data exists, how it's stored, validated, retrieved, and by whom.*

```
HTTP Request → Pydantic Schema → Service → Repository → SQLAlchemy Model → PostgreSQL
```

## 16. Database Design

Design the data model **before** the API — changing a database schema later is expensive; changing a route handler is not.

**Entities (initial):** `users`, `urls`. **Later:** `clicks`, `api_keys`.

- **Primary keys:** Smolink uses Snowflake IDs (see §32), not naive auto-increment (predictable, and doesn't work cleanly across multiple instances without coordination).
- **Foreign keys:** store `user_id` on `urls`, not duplicated user data.
- **Constraints:** unique alias, unique email, `NOT NULL` on required fields — the database is the last line of defense against bad data.
- **Indexes:** the redirect path (`GET /{short_code}`) is the single most latency-sensitive query in the system — index `short_code`. Indexes speed reads at the cost of extra storage and slightly slower writes; add them where a real query pattern justifies it, not everywhere.
- **Normalization:** avoid duplicating data (e.g. don't store `username` on every `url` row — join through `user_id`).

**Choosing data types (Smolink-specific):**

| Field | Type | Why |
|---|---|---|
| `expires_at` | `TIMESTAMP WITH TIME ZONE` | Users and servers may be in different time zones; storing without TZ creates silent bugs the moment the app or a user crosses one |
| Snowflake IDs | `BIGINT` | 64-bit by design; `INTEGER` overflows |
| `custom_alias` | `VARCHAR(n)` with a sane max length | Bounded, indexable; `TEXT` works but signals "unbounded," which aliases aren't |
| Future analytics metadata | `JSONB` | Schema-flexible for fields you don't want to migrate for every new tracked attribute (e.g. UTM params) — but don't reach for this before you have an actual variable-shape field |

## 17. SQLAlchemy Models

Models represent tables: columns, relationships, indexes, constraints. A model knows a `URL` has an `expires_at` column — it does **not** know how short codes are generated. That's the service layer's job.

## 18. Pydantic Schemas

**Models represent the database. Schemas represent the API. Never conflate them** — a `User` model has `password_hash`; a `UserResponse` schema must not, or you leak it to every client that fetches a user. Typical schema variants: `Create`, `Update`, `Response`, `Public`, `Internal`.

## 19. Repository Pattern

All SQL lives here, nowhere else. A repository does: insert, update, delete, search, paginate, filter. It never generates Snowflake IDs, validates business rules, returns HTTP responses, hashes passwords, or issues JWTs — those belong to the service layer. This isolation is what lets the database be swapped or mocked without touching business logic.

## 20. Database Migrations (Alembic)

Never hand-edit a production schema. Every change is a version-controlled migration:

```
Modify SQLAlchemy model → generate migration → review it → apply it → schema updated
```

Never: edit production tables manually, delete migration history, or modify an already-deployed migration (write a new one instead).

---

# Part 4 — Business Logic

*The service layer is the brain — where "what should happen" gets decided.*

## 21. Service Layer

Without it, routes balloon into 500-line functions doing validation, ID generation, encoding, DB writes, and cache updates all at once. The service layer exists to absorb that: it validates business rules, coordinates repositories, calls Redis, generates IDs/QR codes, and owns workflow decisions. It never writes SQL, receives HTTP requests, returns HTTP responses, or imports FastAPI.

## 22. Utility Layer

Pure, reusable, no side effects — Base62 encoding, the Snowflake generator, password hashing, date helpers, validators. Test: *could another project reuse this with zero modification?* If yes → utility. If it needs the database or app context → service.

## 23. Validation Strategy — defense in depth, never just one layer

| Level | Where | Example | Trustworthy alone? |
|---|---|---|---|
| 1 | Frontend | Empty field check | No — improves UX only |
| 2 | Pydantic schema | URL/email format, types | Mostly, but not business-aware |
| 3 | Service layer | "Alias already exists," "user owns this URL" | This is where business rules live |
| 4 | Database constraints | Unique alias, foreign keys, NOT NULL | Yes — last line of defense |

## 24. Error Handling

Predictable failure beats surprising failure. Use custom exceptions (`AliasAlreadyExists`, `URLExpired`, `UserNotFound`) caught by a **global exception handler** rather than scattering `try/except` through every route — this gives consistent response shapes and centralized logging for free.

## 25. Logging

Never `print()` in production. Levels: `DEBUG` (dev detail) → `INFO` (normal ops: user logged in, URL created) → `WARNING` (recoverable: Redis down, falling back to DB) → `ERROR` (operation failed) → `CRITICAL` (app can't continue). Log structured data (timestamp, user, request ID, endpoint, status, duration), not bare strings. **Never log** passwords, JWT secrets, API keys, or other sensitive headers/PII.

---

# Part 5 — API Layer

*The receptionist, not the department that solves the problem.*

```
Browser → HTTP → API layer → Service layer → Repository → Database → back up → HTTP response
```

## 26. Route Organization

One file per domain (`urls.py`, `auth.py`, `users.py`, `analytics.py`, `health.py`) — never one 2000-line `main.py`. Routes receive, validate shape, call service, return response. They never write SQL, generate IDs, validate business rules, hash passwords, issue JWTs, or call Redis directly.

## 27. API Endpoints

Resource-oriented, not action-oriented: `GET /api/me/urls` not `/getUserURLs`. **The full, current endpoint list lives in `README.md`** — don't let this section drift into a second copy of it.

## 28. Authentication & Authorization

**Authentication** = who are you (JWT after login). **Authorization** = are you allowed (e.g. deleting someone else's URL → `403`, not `401`). Guests can create/redirect/QR-generate; they cannot access dashboard, delete, or view analytics — those require a JWT.

```
Register → Login → receive access token → stored client-side
→ sent as Authorization: Bearer <token> → validated per request on protected routes
```

## 29. File Uploads *(future)*

Not needed for v1. Later candidates: QR logo upload, CSV import for bulk shortening, custom favicon. Involves multipart form handling, streaming, and storage — deliberately deferred.

## 30. API Versioning

Not needed while there's a single first-party frontend. Becomes necessary the moment there's a public API with external consumers you can't force to upgrade simultaneously — at that point, new breaking changes go to `/api/v2/...` while `/api/v1/...` keeps working for existing clients. (Whether Smolink adopts the `/api/v1/` prefix *now*, pre-emptively, is still an open question — tracked in `SMOLINK_CONTEXT.md`.)

---

# Part 6 — Core Smolink Features

For every feature: why it exists, what it needs from the DB, what the request flow looks like, and what breaks it.

## 31. URL Shortening

`POST /api/urls` → validate schema → validate business rules (alias available, expiry sane) → generate ID → encode → persist → return short URL. Works identically for guests and logged-in users; the only difference is whether `user_id` is populated.

## 32. Snowflake IDs

Why not auto-increment? Auto-increment is predictable and requires DB coordination across multiple instances. A Snowflake ID packs **timestamp + machine ID + sequence number** into a 64-bit integer — unique, roughly sortable by creation time, and generated without a database round-trip, which matters once there's more than one FastAPI instance.

## 33. Base62 Encoding

Converts the (large) Snowflake integer into a short, URL-safe string using `[0-9A-Za-z]` (62 characters) — compact, no special characters that need escaping, human-typeable.

## 34. Custom Aliases

Validated for length, allowed characters, and **reserved words** (`login`, `register`, `admin`, `health`, `metrics`, `api`, `me`, `dashboard` — anything that would collide with a real route must never be assignable as an alias). On conflict: `409`, and per the decision in `SMOLINK_CONTEXT.md`, **no separate availability-check endpoint** — the create call's `409` is sufficient for v1.

## 35. Expiring Links

`expires_at` is a nullable timestamp. Enforced **at read time** on the redirect path (`WHERE expires_at IS NULL OR expires_at > now()`), returning `410 Gone` if expired — not via a scheduled job. Redis TTL is set to match `expires_at` on write so the cache self-evicts at the same moment.

**Data retention policy** (decided in this project's own design discussion, not in the original source material): expiring a link is not the same as deleting it. The `url` row and its aggregate stats (`total_clicks`, `last_clicked_at`) persist indefinitely unless the user explicitly deletes the link via `DELETE /api/me/urls/{id}`. Only raw, granular `click_events` are candidates for a cron-based prune job, and only after a long retention window (e.g. 90 days) — because that's disposable detail, not the aggregate. **Principle: raw event data is disposable, aggregates are not.**

## 36. Redirect Flow

The single most performance-critical endpoint in the system.

```
GET /{short_code} → NGINX → FastAPI → Redis
  cache hit  → 302 immediately, click event published async
  cache miss → PostgreSQL → populate Redis → 302
```

Uses `302` (temporary) rather than `301` (permanent) initially, since destination URLs may be edited — a `301` risks browsers caching a redirect that's no longer accurate.

## 37. QR Code Generation

`GET /api/urls/{short_code}/qr` → generate PNG → return image. Future: logo embedding, color customization, SVG output.

## 38. Click Analytics

Captured per redirect: timestamp, browser, OS, device, referrer, user-agent, IP hash (never raw IP — see security notes in Part 1). Initially written synchronously; the moment this measurably slows the redirect path, move it to a queue (Kafka) consumed by a separate analytics worker — this is the one genuine service-extraction candidate in the whole system, because it's naturally async and decoupled from the redirect's response.

---

# Part 7 — Performance & Scalability

*Production-inspired, not strictly necessary at current scale — the goal is understanding when each optimization earns its keep.*

## 39. Redis Caching — Cache-Aside Pattern

```
Request → Redis → hit? → yes: return
                       → no: PostgreSQL → write to Redis → return
```

**Cached:** `short_code → destination_url` initially; later, dashboard stats and hot analytics. **Invalidation:** on update, write the DB first, then delete the stale cache key — never write-through to Redis as if it were authoritative. Postgres remains the source of truth at all times.

## 40. Background Tasks

Move slow work out of the request/response path: QR generation, email verification, analytics aggregation, cleanup. Start with FastAPI's built-in `BackgroundTasks`; graduate to Kafka workers only once there's a real throughput or reliability reason to.

## 41. Rate Limiting

Redis-backed counter per user/IP; exceeding the limit returns `429`. Suggested starting tiers: guests lower, authenticated users higher — exact numbers are a config decision, not an architectural one.

## 42. Async Programming

Use `async`/`await` for I/O-bound work (DB, Redis, outbound HTTP, file I/O) — while one request waits on I/O, the event loop serves others. **Not** a tool for CPU-bound work (heavy computation still blocks the event loop regardless of `async`).

## 43. Performance Optimization — measure before optimizing

Fix order, in priority: **slow SQL → indexes → caching → Python-level optimization → horizontal scaling.** Metrics worth tracking: average and p95/p99 response time, requests/sec, DB query time, Redis hit ratio, CPU/memory. Never optimize based on a hunch — profile first.

---

# Part 8 — Frontend Architecture & Integration

*The frontend talks to the backend exclusively over HTTP APIs — never directly to Postgres or Redis.*

## 44. Frontend Project Structure

```
frontend/src/
├── assets/       # images, fonts, icons
├── components/   # reusable UI (Button, Modal, QR dialog, Copy button...)
├── pages/        # one per route: Home, Dashboard, Login, Register, Analytics, 404
├── layouts/      # Navbar, Sidebar, Footer, Protected layout wrapper
├── services/     # API calls only — urlService.ts, authService.ts, analyticsService.ts
├── hooks/        # useAuth, useTheme, useDebounce, usePagination
├── contexts/     # global state: auth, theme, notifications
├── router/       # path → page mapping
├── types/        # TS interfaces: URL, User, Analytics, JWT
└── utils/        # copy-to-clipboard, date formatting, client-side URL validation
```

`services/` is the only place `fetch`/`axios` calls live — never scattered across components. One shared base URL (env-driven: `localhost:8000` in dev, the production domain in prod), shared error handling, shared auth header injection.

## 45. Frontend ↔ Backend Communication

```
User action → React component → service function → fetch() → FastAPI → JSON → React state → re-render
```

## 46. Authentication Flow

Guests skip this entirely (create → receive short URL → done). Registered: register/login → receive access token → store client-side → attach as `Authorization: Bearer <token>` on every request to a protected route. If unauthenticated and hitting a protected page (`/dashboard`, `/profile`), redirect to `/login`.

## 47. Frontend Error Handling

| Backend response | Frontend behavior |
|---|---|
| `409` | "Alias already taken" |
| `422` | Highlight the invalid field |
| `401` | Token expired → redirect to login |
| `500` | Generic toast: "Something went wrong" |

Always show a loading state on submit (prevents double-clicks/double-submits) and an explicit empty state ("No shortened URLs yet") rather than a blank screen.

## 48. State Management

**Local** (one component: input value, modal open/closed) vs. **global** (shared: current user, theme, auth) vs. **server state** (lives in Postgres, fetched into React: dashboard, analytics, URL list — this is the state most likely to go stale and need explicit refetch/invalidation logic).

---

# Part 9 — Quality Assurance & Testing

*A feature isn't done when it compiles — it's done when it's verified and protected against regression.*

## Testing Pyramid

Unit tests (many) → integration tests (fewer) → manual testing (least, for things automation covers poorly: animations, responsiveness, accessibility).

## 49. Unit Testing

Tests one function in isolation — no real DB, no HTTP, no Redis; dependencies are mocked. Good candidates: `generate_short_code()`, the Base62 encoder, URL validators, business-rule functions.

## 50. Integration Testing

Real components working together — e.g. `POST /api/urls` exercising service → repository → actual test database → response, end to end.

## 51. API Testing

For every endpoint, test: correct request, invalid request, unauthorized, forbidden, missing resource, duplicate resource, and unexpected failure. Concretely for Smolink: `POST /api/urls` → `201`; duplicate alias → `409`; malformed body → `422`; `GET /api/me` without a JWT → `401`; deleting someone else's URL → `403`; redirect on an expired link → `410`; on a missing one → `404`.

## 52. Debugging Strategy

Reproduce → identify which layer (frontend/API/service/repository/DB/Redis) → read logs (don't guess) → inspect the actual request (headers, body, JWT, params) → inspect the DB state → fix only once the cause is understood → **add a regression test for every bug fixed.**

**Common mistakes to avoid:** testing only happy paths, skipping auth tests, one giant test function instead of focused ones, testing implementation details instead of observable behavior. Coverage isn't the goal — meaningful tests on critical paths (auth, money-adjacent logic, business rules) are worth more than 100% coverage of trivial getters.

---

# Part 10 — DevOps & Deployment

*Making the application reliable, repeatable, secure, and reachable — not just "runnable on my laptop."*

```
Local dev → Git → GitHub → Docker → Docker Compose → Oracle Cloud VM → NGINX → HTTPS → public
```

## 53. Git Workflow

Commits represent one meaningful change (`Implement URL shortening`, not `fix`/`update`/`changes`). Branch strategy: `main` initially; `feature/*` branches once the project has enough surface area to need them.

## 54. Docker

Solves "works on my laptop, fails on the server" by packaging the app with its exact dependencies and runtime, so it behaves identically everywhere it runs.

## 55. Docker Compose

Runs backend + Redis + PostgreSQL + NGINX together with one command, handling inter-container networking, volumes, and env vars — instead of starting each service manually.

## 56. Environment Variables

`.env` for real secrets (database URL, JWT secret, Redis URL) — **never committed.** `.env.example` is the committed template with placeholder values, so contributors know what's needed without seeing real credentials.

## 57. NGINX Reverse Proxy

Sits in front of FastAPI: terminates HTTPS, routes requests, handles compression and security headers, and will handle load balancing once there's more than one FastAPI instance.

## 58. HTTPS

Without it, credentials travel in plaintext and are readable by anything on the network path. TLS certificates (e.g. via Let's Encrypt through NGINX) are non-negotiable for anything handling login.

## Deployment Checklist

Backend builds · frontend builds · containers start · DB reachable · Redis reachable · NGINX configured · HTTPS enabled · env vars loaded · `/health` responds · logs visible.

## Common Production Problems

| Symptom | Likely cause |
|---|---|
| Container won't start | Missing env variable |
| DB unreachable | Wrong connection string |
| 502 Bad Gateway | NGINX can't reach FastAPI |
| App crashes | Check logs first, always |
| HTTPS not working | Certificate misconfiguration |

---

# Parts 11–14 — Planned (content pending)

Structure reserved, not yet written up — filling these in is future work, not a fabricated placeholder:

- **Part 11 — Cloud Deployment:** Oracle Cloud specifics, VM setup, PostgreSQL/Redis deployment, monitoring, backup strategy.
- **Part 12 — Distributed Systems:** scaling FastAPI, load balancing, Kafka, horizontal scaling, database sharding, relevant CAP theorem tradeoffs, future microservices extraction.
- **Part 13 — Coding Standards:** naming conventions, file responsibilities, code style, design patterns in use, common mistakes, PR review checklist.
- **Part 14 — Feature Development Workflow:** the end-to-end lifecycle of shipping a feature, worked through concretely for shortening, auth, Redis, and analytics as they were each added.
