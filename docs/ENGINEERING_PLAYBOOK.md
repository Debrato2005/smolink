# Smolink Engineering Playbook

This reference explains backend concepts through Smolink. Many concepts also
apply to Django, Express, Spring Boot, and other frameworks.

Use the [README](../README.md) for architecture decisions and target contracts.
Use the [walkthrough](codebase-walkthrough.md) for implemented behavior and the
[development guide](development.md) for procedures. The
[checklist](backend-build-checklist.md) records verification and next milestones.
[Agent tooling](agent-tooling.md) explains skills and Graphify.

The sections below include future designs. A dependency or design example
does not establish implementation. Resolve status against source and the
walkthrough. If a design conflicts with a README decision, record and resolve
the conflict before implementation.

## Contents

- [Project foundation](#project-foundation)
- [Backend fundamentals](#backend-fundamentals)
- [Data layer](#data-layer)
- [Business logic](#business-logic)
- [API layer](#api-layer)
- [URL features](#url-features)
- [Performance and scale](#performance-and-scale)
- [Frontend design](#frontend-design)
- [Testing and debugging](#testing-and-debugging)
- [Deployment](#deployment)
- [Future reference topics](#future-reference-topics)

## Project foundation

Smolink maps long URLs to compact lookup codes. The project develops backend
engineering judgment through incremental implementation. Each technology needs
a current problem or a specific learning objective.

Primary learning areas include Representational State Transfer (REST) APIs,
architecture, database design,
authentication, caching, containers, continuous integration and delivery
(CI/CD), cloud deployment, monitoring, and distributed systems. The repository
also serves as a portfolio, personal reference, and experimentation project.

The target guest experience includes URL creation, aliases, expiry, redirects,
and QR codes. Registered users also receive owner management and analytics.
Search and pagination belong to owned URL listing. API keys and country-based
analytics remain future options. Authentication is optional for creation.

| Requirement | Design direction |
|---|---|
| Redirect performance | Cache lookups and measure redirect latency |
| Scale | Support multiple instances when needed. Coordinate IDs and shared state first |
| Reliability | Use PostgreSQL when redirect caching fails. Fail protected writes closed when limiting fails |
| Maintainability | Separate HTTP, policy, and SQL ownership |
| Security | Hash passwords, validate input and tokens, use parameterized SQL |
| Observability | Plan logs, metrics, and measured performance |

The backend uses Python, FastAPI, Pydantic, async SQLAlchemy, Alembic,
PostgreSQL, Redis, JSON Web Tokens (JWTs), Argon2id, and HTTPX. Docker Compose
runs the local database services. QR and user-agent dependencies are installed,
but their endpoint features remain pending.

React, NGINX, GitHub Actions, Prometheus, Grafana, and an Oracle Cloud Ubuntu
virtual machine belong to later product and deployment work. Kafka and an
analytics worker require evidence that synchronous capture harms redirects.

## Backend fundamentals

### Network request lifecycle

For a future HTTPS deployment behind NGINX, a typical HTTP/1.1 or HTTP/2
redirect request follows this sequence:

1. The Domain Name System (DNS) resolves the application hostname to an IP address.
2. The browser establishes a Transmission Control Protocol (TCP) connection, normally on port `443` for HTTPS.
3. Transport Layer Security (TLS) negotiates encryption before application data exchange.
4. The browser sends a request such as `GET /abc123`.
5. NGINX terminates TLS and forwards the request to FastAPI.
6. FastAPI resolves the URL and returns a redirect response.
7. The browser follows the redirect destination.

This example describes the planned deployment. Local development connects
directly to FastAPI. HTTP/3 uses a different transport sequence.

### HTTP and REST

A request can carry a method, path, headers, body, and query parameters.
A response carries a status, headers, and an optional body.

| Method | Intended action | Idempotent semantics |
|---|---|---|
| `GET` | Read a resource | Yes |
| `POST` | Create or process a resource | Not guaranteed |
| `PUT` | Replace a resource | Yes |
| `PATCH` | Update selected fields | Depends on the operation |
| `DELETE` | Remove a resource | Yes |

Idempotency concerns the intended resource effect. Repeated requests can still
produce different statuses, logs, or analytics events. Smolink plans `PATCH`
for destination and expiry updates. Keep resource names in paths and use HTTP
methods for actions. Authentication flows have their documented action paths.

Use the README for endpoint status and response contracts. Current examples
include `201` for URL creation, `409` for an alias conflict, `422` for request
validation, and `429` for a denied limit. Future redirects use `302`, unknown
codes use `404`, and expired links use `410`. A limiter outage returns `503`.

JWTs do not make Smolink's authentication fully stateless. Refresh lifecycle
state and current-user authorization remain in PostgreSQL. Shared persistence
lets multiple instances use that state without private in-memory sessions.

### Layers and dependencies

The usual persisted workflow is:

```text
HTTP → API schema → service → repository → SQLAlchemy model → PostgreSQL
```

Health checks need no repository. Cache hits and dependency failures can take
other paths. The pipeline does not imply that every request queries every layer.

| Layer | Owns | Excludes |
|---|---|---|
| API | HTTP translation, request dependencies, transaction boundary | SQL and business policy |
| Schema | Input/output shape and validation | Persistence workflows |
| Service | Business rules and workflow coordination | HTTP responses and direct SQL |
| Repository | Queries, inserts, updates, deletes | Business policy and transaction commit |
| Database | Durable records and constraints | HTTP behavior |

Smolink uses shared layer directories, with files grouped by domain.
A domain accesses another domain through its service interface. Do not add a
second directory layout per domain.

FastAPI `Depends()` resolves request dependencies such as sessions, users,
and limiters. Overrides let tests replace those resources. A database session
belongs to one request. A generator is reusable local state, but its sequence
must be coordinated with other generators.

### Configuration

Typed settings read environment variables and a local `.env` file.
`get_settings()` caches the first instance. Package metadata belongs in
`pyproject.toml`. Secrets belong in deployment configuration or an ignored
local environment file. Use the development guide for setup and the
walkthrough for each setting's meaning.

## Data layer

### Schema design

Model durable relationships before exposing API contracts. Schema changes can
require migration and data conversion. The initial entities are `User`, `Url`,
and `ClickEvent`. Auth adds identity, refresh, opaque-token, and authorization
request records. `api_keys` remains a future entity.

- Numeric primary keys use Snowflake IDs. They require generator coordination.
- `urls.owner_id` references `users.id` without duplicating user data.
- `short_code` and normalized email are unique.
- Required fields use `NOT NULL`. Services also enforce policy.
- Indexes support observed or planned queries and cost storage and write work.

| Data | Current type or representation | Purpose |
|---|---|---|
| Snowflake primary keys | `BIGINT` | Store application-generated integers |
| `expires_at`, `last_clicked_at` | Timezone-aware timestamps | Compare expiry and report activity |
| `short_code` | `VARCHAR(64)` | Store a generated code or alias |
| `total_clicks` | `Integer` | Planned aggregate without scanning events |
| `ip_hash` | Keyed hash string | Planned limited abuse analysis without raw IP storage |
| `(url_id, clicked_at)` | Composite index | Date-range click queries |
| Future variable analytics fields | Possible `JSONB` | Only if variable-shape metadata is needed |

Timezone-aware timestamps represent instants. They do not retain a user's
original timezone name. SQLAlchemy `onupdate=func.now()` applies through its
update path. It is not an independent database trigger.

User deletion sets URL ownership to `NULL`. URL deletion permanently cascades
to click events in v1. Restoration would require a new product decision.

### Models, schemas, and repositories

SQLAlchemy models define tables, fields, indexes, and constraints. A `Url`
model does not generate a short code. That operation belongs to the service.
Pydantic schemas define API data and validation. `PublicUserResponse` excludes
password hashes and internal authentication state.
Common schema roles include create input, update input, public response, and
internal data. Separate those roles when their fields or access rules differ.

Repositories own SQL operations such as insert, lookup, filtering, and updates.
They do not hash passwords, issue tokens, generate IDs, return HTTP responses,
or commit. `flush()` sends pending SQL within a transaction. The route's
`commit()` makes a completed workflow durable.
Repository interfaces separate SQL ownership from business policy. Prefer real
database integration for persistence behavior. Use an isolated replacement only
when it adds distinct fault-detection or diagnostic value.

### Migrations

Use the [migration procedure](development.md#new-migrations). Review generated
operations before execution. Do not edit an applied migration or manually
alter a deployed schema. Create a new revision instead.

## Business logic

Services enforce policy and coordinate repositories. Examples include future
expiry checks, alias selection, password login, and refresh rotation. Keep
SQL and HTTP response translation in their owning layers.

Utilities supply reusable operations such as Base62, password hashing, alias
validation, and ID generation. Some are pure functions. Random-token helpers
and the Snowflake generator have randomness or local state. A utility must not
require a database session or FastAPI request.

### Validation

| Boundary | Check | Limitation |
|---|---|---|
| Frontend | Empty fields and immediate feedback | Clients can bypass it |
| Pydantic | URL/email format, type, password length | Does not establish ownership or uniqueness |
| Service | Expiry, account state, aliases, ownership | Concurrent requests can race |
| Database | Unique values and foreign keys | Does not replace all business rules |

### Errors and logs

Domain exceptions identify expected failures. The URL service uses
`AliasTakenError` and `InvalidExpiryError`. Current routes map these failures
locally. Global domain handlers are a target, not an implemented facility.
Keep expected client failures distinct from unexpected server errors.

Planned structured logs include timestamp, request ID, endpoint, status, and
duration. Choose a level for the event: `DEBUG` for diagnostic detail, `INFO`
for normal operations, `WARNING` for recoverable failures, `ERROR` for failed
operations, and `CRITICAL` when the application cannot continue.
Never log passwords, tokens, secrets, sensitive headers, or unnecessary
personally identifiable information (PII).
Use a logger for production diagnostics. Do not substitute `print()` for
structured application logs.

## API layer

Group routes by domain file. The current files include `urls.py` and `auth.py`.
`/health` remains inline in `main.py`. Future user or analytics files are
examples of organization, not existing modules.

Use the README's single endpoint table. Public code lookup and numeric owner
management routes have different access rules. Preserve `/api/v1` when adding
application APIs. Introduce `/api/v2` for a breaking contract and keep existing
clients' version available.

### Authentication and authorization

Authentication identifies the requester. Authorization checks permitted actions.
Missing or invalid access tokens return `401`. Wrong-owner operations are
planned to return `403`. Guests can create URLs. Redirect and QR access are
planned to remain public. Management and analytics require an authenticated owner.

Local authentication follows:

```text
Register → verify email → login → receive access and refresh JWTs
Bearer access JWT → validate claims → load current user → protected route
```

Access tokens include identity and validation claims. Current-user lookup also
checks verification and `auth_version`. Refresh records support rotation,
reuse detection, and revocation. Logout blocks future refreshes. Password reset
also invalidates old access tokens through `auth_version`.

Passwords use Argon2id. Five consecutive failed password attempts lock an
account for 15 minutes. Successful verified login resets failure state.
Verification and reset tokens are one-time and expiring. See the
[authentication design](superpowers/specs/2026-08-01-authentication-authorization-design.md)
for target details and remaining gaps.

Google OpenID Connect (OIDC) is planned. It requires state binding, PKCE
(Proof Key for Code Exchange), nonce, signature and claim checks, and verified
email. Matching verified email links to an existing local user. This policy
does not establish that Google sign-in works today.

The security checks answer different questions in the planned flow:

| Mechanism | Check | Purpose |
|---|---|---|
| State and browser binding | Returned state matches the authorization attempt bound to this browser | Correlate the callback and resist login CSRF (cross-site request forgery) |
| Nonce | ID-token nonce matches the stored nonce for this attempt | Reject an ID token from another authentication attempt |
| PKCE | Google's token endpoint checks the verifier against the original S256 challenge | Require the verifier when exchanging the code |
| Expiry | Current time is before `expires_at` | Limit the lifetime of an abandoned attempt |
| Consumption | `consumed_at` is still `NULL` before consumption | Reject reuse of the same attempt |

For example, Alice starts a login bound to her browser. Bob sends Alice a
callback for Bob's login. Matching Bob's state to a database row is insufficient.
Smolink must also check the binding to Alice's initiating browser.

If the current attempt expects nonce `NEW_VALUE`, an ID token containing
`OLD_VALUE` fails the nonce check. Signature validation alone does not replace
that check.

For S256 PKCE, the challenge is Base64url of SHA-256 of the ASCII verifier,
without padding. The challenge is public. The verifier remains secret until
the code exchange. An intercepted code alone does not satisfy the verifier check.
Google also enforces its authorization code's expiry and single-use lifecycle.
Smolink's authorization-attempt record has a separate consumption lifecycle.

An attempt created at `10:00` with the target ten-minute lifetime expires at
`10:10`. A callback at `10:20` fails expiry validation. These examples describe
the target protections, not an implemented Google flow.

IP and account limits also address different scopes. Distributed attempts can
use many IP addresses. PostgreSQL account-failure state tracks consecutive
password failures against the same account across those addresses.

File uploads remain outside v1. Possible later features include QR logos,
CSV imports, and custom favicons. They require upload validation and storage.

## URL features

### Shortening, IDs, and aliases

URL creation validates input, checks expiry, generates an ID, chooses a code,
and persists a URL. `owner_id` distinguishes guest and owned URLs. Guest and
user requests also use separate rate-limit scopes.

Base62 represents an integer with digits and letters. The implementation's
alphabet is `0-9`, then `a-z`, then `A-Z`. This ordering matters for encoding.
Generated codes are not secret access credentials.

Aliases normalize to lowercase and allow 3–64 letters, digits, or hyphens.
Reserved names protect root routes. Legacy auth names remain reserved.
A conflict returns `409`. There is no separate availability check in v1.

### Planned expiry and redirects

Creation rejects non-future expiry. The redirect feature will check expiry at
read time. It must distinguish an unknown code (`404`) from an existing
expired URL (`410`). Filtering expired rows out of the only lookup would lose
that distinction.

Cache entries must carry `url_id`, destination, and expiry. Their lifetime must
not exceed link expiry or the configured cache lifetime. Update and delete
must write the database first, then invalidate stale cache entries.

The planned redirect flow is:

```text
GET /{short_code}
  cache hit  → check expiry → record click → 302
  cache miss → PostgreSQL → check expiry → cache → record click → 302
  cache error → PostgreSQL fallback
```

`302` permits destination changes without a permanent browser redirect.
A redirect does not delete an expired URL. The row and aggregates remain until
explicit URL deletion, or cascading rules apply. Raw event pruning is a future
option after a documented retention window, such as 90 days. That example is
not an implemented retention policy.
Under this target, URL rows and aggregates persist without an automatic expiry
deletion schedule. Raw event retention and aggregate retention are separate
decisions. A future raw-event prune must preserve the aggregate counters.

### Planned QR and analytics

The QR route will generate a PNG for the public short URL. Logo embedding,
colors, and SVG are later options. PNG generation remains on demand in the
current target. Moving it to background work needs a separate contract.

Click capture will derive browser, operating system, and device from the
user-agent header. It stores those derived values, referrer, click time, and a
keyed IP hash. The schema does not store raw user-agent text or raw IP.
Owner reports will include totals, daily series, and dimension breakdowns.
Measure synchronous capture before extracting an analytics consumer.

## Performance and scale

### Cache-aside and failure policy

Cache-aside reads Redis first and PostgreSQL on a miss. Cache failure also
falls back to PostgreSQL. Redis never replaces the durable URL record.
Dashboard caching is a later option. It requires its own invalidation design.

Rate-limit state has a different purpose. The atomic Redis log rejects a
protected write when its allowance is exhausted. An unavailable limiter returns
`503`, so writes cannot bypass abuse controls during an outage.
Per-account password lock state remains durable in PostgreSQL.

### Rate-limit algorithm comparison

| Algorithm | Mechanism | Tradeoff |
|---|---|---|
| Fixed window | One counter per time bucket | Small state. Adjacent buckets can allow a boundary burst |
| Sliding-window log | Timestamp per allowed request | Exact window enforcement. State grows with accepted requests |
| Sliding-window counter | Weighted current and previous counts | Less state than a log. Counts approximate the window |
| Token bucket | Refill tokens at a fixed rate | Allows bounded bursts with a long-term rate |
| Leaky bucket | Process queued work at a constant rate | Smooths traffic but can increase queue latency |

For example, a fixed limit of 100 per minute can allow 100 requests just before
one boundary and 100 just after it. Smolink chose the sliding-window log for
its protected writes. Token buckets are a different policy, not the current
recommendation for this implementation.

### Async work and background tasks

`async`/`await` lets other requests progress while compatible I/O waits.
CPU work and blocking libraries can still block an event loop. The `async`
keyword alone does not make password hashing or computation nonblocking.

The current email sender awaits HTTPX after database commit. It does not use
FastAPI `BackgroundTasks`. In-process background tasks can handle suitable
non-durable work. Reliable retries or measured throughput needs can justify a
worker. Do not silently move verification or required capture out of an atomic
workflow.

### Measurement

Inspect slow SQL first, then indexes, caching, application CPU costs, and
scaling needs. Measure average and p95/p99 response time, requests per second,
database time, cache hit ratio, CPU, and memory. This order is a diagnostic
starting point, not a guarantee that every problem has the same cause.

## Frontend design

The frontend remains planned. It communicates through HTTP APIs and must not
connect directly to PostgreSQL or Redis.

The [canonical frontend design system](frontend-design-system.md) turns the
visual direction into enforceable tokens, component rules, page intensity,
motion limits, and review checks. It uses three layers:

- Neobrutalism supplies the shared component grammar.
- Bauhaus supplies the grid, hierarchy, functional alignment, and asymmetric
  macro-composition.
- Pop Art supplies limited flat-color and print-inspired accents.

This separation supports maintainability. Shared neobrutalist primitives stop
page-level styling forks. A rational grid keeps forms and dense views usable.
Limited Pop Art gestures prevent decoration from competing with content. The
result can remain recognizable while marketing, authentication, and dashboard
pages use different intensity.

Accessibility and task completion take precedence over expression. The system
targets WCAG 2.2 Level AA, uses tested color pairs, keeps keyboard focus outside
thick borders, and requires state cues beyond color. Exact requirements belong
in the design-system document rather than this rationale.

Suggested React directories include `assets`, `components`, `pages`, `layouts`,
`services`, `hooks`, `contexts`, `router`, `types`, and `utils`. Centralize
API calls, base URL, error parsing, and access-token attachment in services.
Use the backend's implemented endpoints when integrating each page.

| Planned directory | Responsibility and examples |
|---|---|
| `assets/` | Images, fonts, and icons |
| `components/` | Shared buttons, dialogs, copy controls, and other interface elements |
| `pages/` | Home, Dashboard, Login, Register, Analytics, and 404 pages |
| `layouts/` | Navbar, sidebar, footer, and protected-page wrapper |
| `services/` | API calls, such as `urlService.ts`, `authService.ts`, and `analyticsService.ts` |
| `hooks/` | Reusable behavior, such as `useAuth`, `useDebounce`, and `usePagination` |
| `contexts/` | Shared authentication and notification state when concrete consumers justify them |
| `router/` | Mapping from paths to pages |
| `types/` | TypeScript contracts for URLs, users, analytics, and tokens |
| `utils/` | Clipboard, date formatting, and client-side validation helpers |

Do not create this complete directory tree in advance. Add a directory when an
authorized feature needs its responsibility.

Use the current component-source order:

1. Use a suitable neobrutalism.dev component through its shadcn registry flow.
2. Otherwise, skin a shadcn-compatible Base UI primitive with Smolink tokens.
3. Create a custom shared primitive only for an unmet Smolink interaction.

The current neobrutalism.dev library uses Base UI rather than Radix UI. Its
September 2026 release also removed dark mode. Recheck the current registry
before adoption because vendor details can change. Dark mode remains deferred
until a product requirement justifies a separate contrast-tested system.

React Bits is optional and subordinate. Paper Shaders is deferred and cannot
supply gradients or ambient decoration. GSAP and Lenis remain conditional for
interactions that materially need them. CSS and native scrolling are the
defaults. These tools cannot define the visual language.

An interface action calls a service, which sends the request and parses the
response. Updating React state then triggers rendering. Keep `fetch` or `axios`
calls in services. Use one environment-backed API base URL.

Guests can create without login. Local accounts must register, verify email,
and log in before protected pages. Define a token storage and refresh policy
before frontend implementation. Attach Bearer access tokens to protected
requests and to URL creation when assigning ownership.
Redirect an unauthenticated visitor from a protected page to login. Guests
can complete URL creation without that login flow.

| API outcome | Planned interface behavior |
|---|---|
| `409` alias conflict | Show that the alias is already taken |
| `422` | Identify invalid fields |
| `401` | Handle invalid/expired authentication and require login when needed |
| `403` | Explain denied access |
| `429` | Show retry guidance from `Retry-After` |
| `503` | Show temporary service failure |
| Unexpected server failure | Show a generic error without internal details |

Show submission progress and prevent duplicate submissions. Show an explicit
empty state instead of a blank dashboard. Distinguish local component state,
shared application state, and server state. Server state needs refresh and
invalidation when the backend changes.

The checklist records frontend milestones and verification. The design-system
document is authoritative for visual and interaction decisions. The
[frontend engineering guide](../frontend/README.md) owns browser state,
transport, privacy, and rendered acceptance.

## Testing and debugging

### Behavior-first testing strategy

The [README testing policy](../README.md#testing-policy) governs test selection.
Use a layered strategy based on observable behavior and realistic system
boundaries. Confidence priority does not prescribe test counts or require
every check to use the broadest possible suite.

**1. End-to-end (E2E) tests:** once the complete product exists, real user
journeys give the highest confidence in its combined behavior. The React
frontend and browser E2E suite do not exist yet. Plan Playwright journeys
against the real application stack where practical, without mocks of internal
application layers. Use controlled data and external-provider doubles for
deterministic, reproducible checks.

Select a small set of critical journeys as the frontend becomes available:

- Guest URL creation and a generated link's redirect.
- Registration, email verification, and login.
- Authenticated creation, dashboard listing, and owned URL editing/deletion.
- QR generation and analytics.
- Logout and recovery from expired or invalid authentication.

These are planned checks, not current coverage. Use direct HTTP integration
for backend-only contracts when it gives equivalent assurance with less setup.
Playwright is not required for those checks.

**2. API/integration tests:** these carry most behavioral confidence during
the current backend-first stage. Exercise real FastAPI routing, validation,
services, repositories, SQLAlchemy, PostgreSQL, and Redis where practical.
Check HTTP contracts, authentication boundaries, durable effects, constraints,
and commit/rollback behavior. For each endpoint, check relevant success,
validation, authentication, authorization, missing-resource, conflict, and
dependency-failure outcomes. Verify Alembic migrations against a separate
empty database rather than treating model metadata as migration evidence.

Existing tests exercise URL creation, alias conflicts, guest/user ownership,
local authentication, refresh rotation and replay revocation, verification,
reset, persistence constraints, and Redis limits. Failure injection also
checks limiter errors. Owner-management authorization, redirect/cache behavior,
QR, analytics, and migration-chain verification remain release work.
Use the [walkthrough](codebase-walkthrough.md#tests-and-verification-limits)
for current test categories and limitations.

**3. Selective unit tests:** isolation is useful when a broader test would be
awkward, slow, ambiguous, or incomplete. Good candidates include Base62,
Snowflake invariants, aliases, deterministic validators, parsing/normalization,
cryptographic helper contracts, pure functions with many edge cases, state
machines, and mathematical or algorithmic logic. Keep useful existing tests.
Test selection does not justify deleting or rewriting a category.

Tests that mirror private structure or merely restate the implementation
often fail during harmless refactors. Heavy mocks can verify mock behavior
while real integration defects remain undetected. These tests add maintenance
cost with little regression protection. Do not test trivial implementation
details or mock every dependency merely to increase isolation or coverage.

A tiny E2E suite alone also leaves gaps. Browser checks can be slower and
operationally complex, and their failures can be difficult to localize.
Focused algorithm and security edge-case tests add fault detection and useful
diagnostics. Retain lower-level tests when they add that distinct value.

### Red → green → refactor and regression cases

For behavior changes and bug fixes, first establish a reproducible failing
check at the highest practical boundary that sufficiently isolates the
requirement. Confirm that it fails for the expected behavior. Implement the
minimum correct change, then rerun focused and relevant broader suites.
Refactor while preserving the tested contract.

| Requirement or bug | Useful failing check |
|---|---|
| Base62 arithmetic | Focused unit test |
| SQL constraint or repository interaction | Real database integration test |
| Authentication workflow or incorrect HTTP status | API/integration test |
| Redis degradation | Integration test with controlled dependency failure |
| Login/dashboard workflow once the frontend exists | Browser E2E test |

Every confirmed bug becomes a regression case when automation can meaningfully
reproduce it. Place the case at the boundary where the bug was observable.
Add a lower-level diagnostic case only when it adds value. Do not manufacture
a unit test before every implementation step. For trivial, configuration-only,
generated, or documentation changes, use relevant checks without fabricating
meaningless tests.

### Mocking and isolation

Prefer real components when they are cheap, deterministic, and under project
control: FastAPI, a PostgreSQL test database, a Redis test instance, SQLAlchemy,
and application services/repositories. Override resource setup for isolation
without replacing the behavior under test.

Mock or fake Resend, Google OAuth/OIDC calls, and other external APIs when real
calls are unsafe, nondeterministic, costly, or inappropriate. Control time when
necessary. Inject genuine failure conditions intentionally. An injected
exception checks error handling, but does not alone prove behavior during a
real network outage. Avoid mocks of internal layers when realistic integration
is practical.

Use isolated database/Redis state and deterministic setup and cleanup.
Use unique records or transaction rollback, and remove committed test data
when necessary. Clear fixed Redis keys before and after the case.
Create, use, and close each async resource within a compatible event loop.
Do not depend on execution order or leftover state.

### Test quality and coding agents

A useful test protects an externally meaningful contract or a high-risk
internal invariant. It fails when that behavior breaks and survives harmless
refactors. Give it a clear purpose and enough failure context for diagnosis.
Avoid private-detail assertions unless those details are required invariants.
Avoid duplicate coverage unless the lower-level case adds diagnostic or
fault-detection value. Coverage percentages identify gaps, but defect detection
is the objective. Test count is not evidence of confidence.

Coding agents can cheaply generate many superficial tests. Do not automatically
add batches of unit tests after implementation. Before adding a test, ask:

1. What failure would it detect?
2. Does a higher boundary already cover that failure?
3. Would it survive an internal refactor that preserves behavior?
4. Is a real dependency practical instead of a mock?
5. Does it materially increase confidence?

### Later reliability verification

Functional tests do not establish production reliability. Relevant future
checks include empty-database migrations, production smoke tests, health and
readiness checks, latency regressions, load, rate limits, security, and
backup/restore. Also verify PostgreSQL/Redis failure paths, dependency failure
injection, and observability against defined service-level objectives (SLOs).
These remain planned verification, not established guarantees.
Smolink is a URL shortener, so this policy does not add LLM/agent evaluation
infrastructure. Manual checks supplement automation for layout, motion,
keyboard interaction, and accessibility.

### Debugging

For a reproducible bug:

1. Reproduce the failure with a focused case.
2. Identify the failing layer from the traceback and logs.
3. Inspect the request and relevant persisted state without exposing secrets.
4. Add a meaningful regression test at the boundary where the bug was observable.
5. Fix the established cause.
6. Run the focused test and relevant shared verification.

Use the development guide for commands. Do not claim a test passed without
execution evidence or an explicit user-reported qualification.

## Deployment

Production deployment remains planned. Local Compose currently starts only
PostgreSQL and Redis. Later deployment needs application images, frontend
builds, NGINX, TLS, secrets, backups, and observability.

Docker images package a runtime and dependencies. They improve repeatability,
but architecture, host settings, and external services can still differ.
Compose can coordinate containers, networking, volumes, and environment values.
That capability does not imply the current file starts the complete product.

NGINX will terminate HTTPS, route requests, and apply relevant headers and
compression. Configure trusted proxy boundaries before enabling production IP
limits. Add load balancing only when multiple instances exist. Use HTTPS for
credentials in transit. Certificate renewal needs its own verification.

Keep commits focused on one meaningful change. Use the branch convention
requested for the task. The project plan starts on `main`, then uses `feature/*`
branches as its feature scope grows. An explicit task convention takes priority.
Never commit real secrets or local volumes.

Release checks must cover builds, container health, database migrations,
Redis, proxy routing, TLS, settings, `/health`, logs, and recovery procedures.
The checklist tracks this work. No production runbook exists yet.

| Symptom | Possible cause or first check |
|---|---|
| Container does not start | Inspect logs for required configuration or runtime failures |
| Database cannot connect | Check network, health, credentials, and connection URL |
| `502 Bad Gateway` | Check proxy connectivity to FastAPI |
| Application crashes | Read the traceback and process logs |
| HTTPS fails | Check certificate, hostname, expiry, and proxy configuration |

These are diagnostic leads, not confirmed causes. Use observed evidence before
changing configuration.

## Future reference topics

- Cloud deployment: Oracle Cloud configuration, backups, restore, and monitoring.
- Distributed systems: multiple instances, load balancing, Kafka, sharding, and CAP tradeoffs.
- Coding standards: names, ownership, patterns, and review rules.
- Feature workflow: worked examples for shortening, authentication, Redis, and analytics.

These topics remain unwritten. Do not describe them as implemented operations.
