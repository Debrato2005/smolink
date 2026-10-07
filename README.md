# Smolink Engineering Context

Smolink is a backend-first URL shortener and an engineering learning project.
This README defines its architecture decisions, invariants, and target API
contracts. Read it before changing code. Record a replacement decision and its
reason before changing an existing decision.

## Documentation

| Document | Use |
|---|---|
| [Development guide](docs/development.md) | Local setup, tests, migrations, and troubleshooting |
| [Codebase walkthrough](docs/codebase-walkthrough.md) | Current implementation and file responsibilities |
| [Backend build checklist](docs/backend-build-checklist.md) | Milestones and dated verification records |
| [Engineering Playbook](docs/ENGINEERING_PLAYBOOK.md) | Design reasoning and future concepts |
| [Frontend design system](docs/frontend-design-system.md) | Canonical visual, component, interaction, and accessibility rules |
| [Frontend engineering guide](frontend/README.md) | Browser, state, transport, privacy, and verification rules |
| [Agent Guide](docs/AGENT_GUIDE.md) | Agent workflow and change rules |
| [Agent tooling](docs/agent-tooling.md) | Skills, writing conventions, and Graphify |
| [Authentication design](docs/superpowers/specs/2026-08-01-authentication-authorization-design.md) | Approved authentication target and known implementation gaps |

The initial data-model design and rate-limiter plan under `docs/superpowers/`
record earlier milestones. Their status notes, example code, and commands
reflect those dates. Use the walkthrough and development guide for current work.

## Project principles and scope

1. Add a technology when it solves a current problem at this project's scale.
2. Follow the roadmap. Add Kafka only after measurements justify an asynchronous workload.
3. Prefer tools with understood behavior and maintenance costs.
4. Keep a specific learning goal when exploring a new tool, such as Rust for a measured latency bottleneck.
5. Record the reason for each architecture decision.

Smolink starts as a modular monolith. It does not target hypothetical traffic
such as millions of requests per second. Service extraction requires evidence
of an asynchronous, independent boundary. Live alias checks, custom domains,
and team workspaces are deferred.

## Architecture decisions

### 1. Layered modular monolith

Redirects are read-heavy and sensitive to latency. URL creation writes less
frequently. A cache can serve redirect lookups within one application.
Separate shortener and redirect services would add a network call. The earlier
design aims for a sub-millisecond application redirect path. This is an
unmeasured target, not an established latency guarantee.

Analytics is a candidate for later extraction. The first release plans to
record click events synchronously. If measurements show an unacceptable
redirect delay, the redirect handler can publish events to a queue for a
separate consumer.

The repository uses shared API, schema, service, repository, and model packages.
It does not use a separate directory tree for each domain. Domain interfaces
control data access. A domain must use another domain's service interface
instead of directly querying that domain's repository.

| Domain | Responsibility | Status |
|---|---|---|
| Shortener | ID generation, Base62 encoding, aliases, URL creation | Implemented |
| Redirect | Cache-aside lookup and click capture | Planned |
| Analytics | Click storage and reports | Table implemented. Capture and reports planned |
| Authentication | Token issuance, verification, and required or optional authentication | Local flows implemented. Google OIDC pending |

### 2. Optional authentication

Guests can create URLs without an account. Guest URLs have `owner_id=None`.
A valid access token assigns `owner_id` to the current user. Dashboard,
management, and analytics routes are planned for authenticated owners.

### 3. PostgreSQL owns durable data

PostgreSQL is the source of truth for URLs, users, and authentication state.
Redis holds redirect-cache entries and ephemeral rate-limit state. Redis must
never be the only store for durable application data.

The planned redirect cache uses cache-aside lookup. If Redis fails, the
redirect path must read PostgreSQL. Protected writes have a different failure
policy: an unavailable rate limiter returns `503`.

### 4. Snowflake IDs and Base62 short codes

The service generates a Snowflake ID and encodes it in Base62. This avoids a
random-code retry loop when generator state is coordinated correctly.
Generators must have distinct worker IDs or shared sequence state to prevent
collisions. The current auth and URL route modules each create a generator
with the same configured worker ID. This remains an implementation gap.

### 5. Alias conflicts use the create endpoint

In v1, `POST /api/v1/urls` returns `409 Conflict` when an alias exists.
There is no alias-availability endpoint or `check_only` flag.
An availability check serves live validation in the interface. Adding that
check to creation would give the create endpoint a second responsibility.

A later live-validation feature can use
`GET /api/v1/aliases/{alias}/availability` with frontend debouncing. That path
is a future option, not an implemented endpoint.

### 6. Route identifiers

- Use `short_code` for public lookup: `/{short_code}` and `/api/v1/urls/{short_code}/qr`.
- Use the numeric `id` for owned resources: `/api/v1/me/urls/{id}`.

Public lookup and ownership checks require different identifiers.

### 7. Health checks

`GET /health` is the current health endpoint. It returns application status,
not database or Redis readiness. Add `/live` and `/ready` when an orchestrator
needs separate restart and traffic-routing signals.

### 8. Redis sliding-window limits

An atomic Lua script enforces rolling 60-second limits in Redis:

| Scope | Redis key | Requests per window |
|---|---|---|
| Auth writes | `rate:auth:{ip}` | 5 |
| Guest URL creation | `rate:create:guest:{ip}` | 10 |
| Authenticated URL creation | `rate:create:user:{user_id}` | 30 |

All current auth POST routes share the auth-write limit. `GET /health` and
`GET /api/v1/auth/me` have no limiter. The planned redirect has no limiter.
Denied requests return `429` with a positive `Retry-After` header in seconds.
If the limiter fails, protected writes return `503`.

Client identity currently comes from `request.client.host`, or `"unknown"`
when absent. Proxy trust and forwarded-header handling remain deployment work.

### 9. Session-backed JWT authentication

Smolink issues JSON Web Token (JWT) access and refresh tokens. Access tokens
are short-lived. Refresh records persist in PostgreSQL to support rotation,
logout, reset, and reuse detection. The database stores a keyed hash of the
refresh JWT identifier (`jti`), not the raw JWT.

Each login creates a refresh-token family. Rotation consumes one record under
a row lock and creates a child in the same family. Reuse of a consumed token
revokes that family. Authorization loads the current user and checks
`email_verified_at` and `auth_version`. Logout blocks future refreshes.
Password reset also increments `auth_version` to reject existing access tokens.

Local registration creates an unverified account and a hashed verification
token in one transaction. The route commits before sending a Resend email.
Email verification is required before local login. Five consecutive password
failures lock the account for 15 minutes.

Verification tokens expire after 24 hours. Password-reset tokens expire after
one hour. Both are single-use. Forgot-password and resend-verification return
the same empty `202` response across account states after successful validation
and limiting. Email-delivery failures are suppressed in those two routes.
Registration email-delivery failures currently propagate after the account commits.

Password reset consumes its token, replaces the Argon2id hash, clears lock
state, increments `auth_version`, and revokes active refresh families atomically.
Optional authentication supports guest and owned URL creation.

Google OpenID Connect (OIDC) remains unfinished. The approved target validates
Google's ID token and verified email, then links a matching local account.
Google configuration and persistence tables exist. They do not establish a
working sign-in flow.

For dated test results, use the [checklist](docs/backend-build-checklist.md#current-verified-state).

### 10. API versioning

Application APIs use `/api/v1`, including authentication. The planned public
`/{short_code}` redirect is the only root dynamic route. Alias reservations
protect `api`, `health`, `docs`, `redoc`, and `openapi.json`. Legacy reservations
remain until a separate compatibility decision removes them.

### 11. Transactions and error translation

Services coordinate multi-record workflows through one shared session.
Repositories flush changes and do not commit. Current routes commit or roll
back the workflow and map domain exceptions to HTTP responses.

Global domain handlers and a shared `ErrorResponse` schema remain targets.
Current domain errors use the envelope below. FastAPI validation and dependency
errors still use `detail`. Do not describe error normalization as complete.
Normalize request-validation errors before release. Preserve the approved
direction toward global domain handlers instead of adding new per-route
domain exception-mapping patterns.

## Testing policy

Test important behavior at the highest realistic boundary that gives useful,
deterministic feedback. Use lower-level tests when they add distinct diagnostic
or fault-detection value. Select tests by risk and observable contracts, not
by a fixed ratio of test categories.

The confidence priority is:

1. **End-to-end (E2E):** highest product confidence once the complete application exists. Browser journeys and Playwright remain planned.
2. **API/integration:** the primary safety net at the current backend-first stage. Exercise FastAPI and real PostgreSQL/Redis behavior where practical.
3. **Selective unit:** protect algorithms, validators, security helpers, and state invariants when isolation adds useful feedback.

For behavior changes and bug fixes, establish a reproducible failing check at
the highest practical boundary that sufficiently isolates the requirement.
Then make the minimum correct change and rerun focused and relevant broader
suites. Red → green → refactor does not require a unit test for every step.
Do not fabricate tests for trivial, configuration-only, generated, or
documentation changes when no meaningful automated behavior check applies.

Every confirmed bug becomes a regression case when automation can meaningfully
reproduce it. Place that case where the bug was observable.
Mock external boundaries intentionally. Avoid mocks of internal Smolink layers
when realistic integration is practical. Coverage is diagnostic, and test count
is not a quality objective. Do not impose arbitrary coverage targets.

See the [behavior-first strategy](docs/ENGINEERING_PLAYBOOK.md#behavior-first-testing-strategy)
for selection criteria, isolation, mocking, and future reliability checks.
The [walkthrough](docs/codebase-walkthrough.md#tests-and-verification-limits)
describes existing tests and their limits.

## Backend roadmap

1. **Foundation:** FastAPI settings, local Compose services, and `/health`.
2. **Data layer:** async SQLAlchemy, Alembic, URL tables, and auth tables.
3. **URL utilities:** Snowflake IDs, Base62, and alias validation.
4. **Rate limiting:** Redis sliding-window limits for auth and URL creation.
5. **Authentication and creation:** local authentication and optional URL ownership, then Google OIDC.
6. **URL features:** owner management, redirects, QR generation, and analytics.
7. **Release verification:** tests and documentation, then frontend and deployment.

The checklist records completion evidence. A target contract does not imply
that its endpoint is implemented.

## Frontend direction

The frontend remains planned. React with TypeScript is the product direction.
The [canonical frontend design system](docs/frontend-design-system.md) defines
the required **Neobrutalism × Bauhaus × Pop Art** visual language:

- Neobrutalism defines shared component structure and interaction.
- Bauhaus defines the grid, hierarchy, alignment, and composition.
- Pop Art supplies limited graphic accents.
- Usability, accessibility, content hierarchy, and task completion take
  precedence over the aesthetic layers.

Use current neobrutalism.dev components through their shadcn and Base UI
workflow when suitable. Skin fallback Base UI primitives with Smolink tokens.
Create a custom shared primitive only when neither source meets the interaction.
Gradients, soft elevation, generic rounded SaaS styling, and uncontrolled
decoration are prohibited. The design-system document owns all exact tokens,
states, intensity levels, source rules, and review checks.

## API standards

Domain errors use:

```json
{"error": "<short code>", "message": "<human readable>"}
```

| Condition | Status |
|---|---|
| Conflict | `409` |
| Request or URL business validation failure | `422` |
| Missing resource | `404` |
| Authentication required or invalid token | `401` |
| Wrong owner or unverified local login | `403` |
| Locked account | `423` |
| Invalid or expired verification/reset token | `400` |
| Exceeded limit | `429` with `Retry-After` |
| Unavailable limiter | `503` |

Planned pagination uses `?page=&limit=`. Search, filter, and sort extend query
parameters. Breaking changes require a new API version.

## Backend endpoints

| Method | Path | Purpose | Status |
|---|---|---|---|
| `GET` | `/health` | Application health | Implemented |
| `POST` | `/api/v1/auth/register` | Register a local account | Implemented |
| `POST` | `/api/v1/auth/login` | Authenticate a verified local account | Implemented |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh tokens | Implemented |
| `POST` | `/api/v1/auth/logout` | Revoke a refresh-token family | Implemented |
| `GET` | `/api/v1/auth/me` | Get the current user | Implemented |
| `POST` | `/api/v1/auth/verify-email` | Consume a verification token | Implemented |
| `POST` | `/api/v1/auth/resend-verification` | Request a replacement email | Implemented |
| `POST` | `/api/v1/auth/forgot-password` | Request a reset email | Implemented |
| `POST` | `/api/v1/auth/reset-password` | Consume a reset token and revoke sessions | Implemented |
| `GET` | `/api/v1/auth/google/start` | Start Google authorization | Planned |
| `GET` | `/api/v1/auth/google/callback` | Validate Google authorization | Planned |
| `POST` | `/api/v1/urls` | Create a guest or owned URL | Implemented |
| `GET` | `/api/v1/me/urls` | List owned URLs | Planned |
| `PATCH` | `/api/v1/me/urls/{id}` | Update an owned URL | Planned |
| `DELETE` | `/api/v1/me/urls/{id}` | Delete an owned URL | Planned |
| `GET` | `/api/v1/me/urls/{id}/analytics` | Get owned URL analytics | Planned |
| `GET` | `/api/v1/urls/{short_code}/qr` | Generate a public QR PNG | Planned |
| `GET` | `/{short_code}` | Redirect to the destination | Planned |

## Project structure

```text
smolink/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # HTTP route handlers
│   │   ├── api/v1/dependencies/ # authentication and rate limits
│   │   ├── core/               # settings and Redis
│   │   ├── db/                 # engine, sessions, declarative base
│   │   ├── models/             # SQLAlchemy tables
│   │   ├── repositories/       # SQL by domain ownership
│   │   ├── schemas/            # Pydantic API contracts
│   │   ├── services/           # business workflows and email delivery
│   │   └── utils/              # ID, encoding, alias, and security helpers
│   ├── alembic/
│   └── tests/
├── docs/                      # maintained guides and dated designs
│   ├── frontend-design-system.md # canonical planned frontend visual rules
│   └── docker-compose.yml     # local PostgreSQL and Redis
├── frontend/                  # frontend engineering guidance and agent skills
└── AGENTS.md
```

## Data model

All current tables use application-generated Snowflake `BIGINT` primary keys.
The current models and migrations define:

- **User:** normalized unique email, nullable Argon2id password hash, verification time, login lock state, `auth_version`, and timestamps.
- **AuthIdentity:** provider and provider subject linked to one user. The provider/subject pair is unique.
- **RefreshToken:** keyed `jti` hash, family UUID, parent relation, expiry, use time, and revocation time.
- **EmailVerificationToken** and **PasswordResetToken:** hashed opaque tokens with expiry and consumption times.
- **OAuthAuthorizationRequest:** hashed state, nonce, raw PKCE verifier, expiry, and consumption time for the planned Google flow.
- **Url:** unique `short_code`, destination, nullable `owner_id`, expiry, click aggregates, and timestamps.
- **ClickEvent:** `url_id`, click time, browser, operating system, device, referrer, and keyed IP hash.

`short_code` stores either a generated Base62 code or a custom alias. There is
no separate `custom_alias` field. `total_clicks` currently uses SQLAlchemy
`Integer`, not `BIGINT`. Click events have a `(url_id, clicked_at)` index.
The table has no raw IP or raw user-agent field.

Deleting a user sets URL `owner_id` to `NULL`. Deleting a URL permanently
cascades to its click events. `updated_at` uses SQLAlchemy `onupdate=func.now()`.
The migrations do not create a trigger for updates made outside SQLAlchemy.

## Invariants

- Keep redirects independent of network calls to another application service.
- Preserve guest URLs with no owner.
- Access another domain's data through its service interface.
- Store durable data in PostgreSQL. Redis enforcement keys are ephemeral.
- Never persist or log plaintext passwords, raw refresh JWTs, reset tokens, verification tokens, or OAuth client secrets.
- Do not issue Smolink tokens to unverified password accounts. Block their login and protected API access.
- Measure synchronous click capture before introducing a queue or worker.

## Future options and open questions

Deferred options include password-protected links, scheduled activation, bulk
shortening, custom domains, team workspaces, tags, collections, and API keys.
Separate liveness and readiness checks depend on orchestration.

The deployment direction is an Oracle Cloud virtual machine. Instance count
and the timeline for multiple instances remain undecided. Generator
coordination, normalized error responses, and Google callback delivery remain
unfinished. See the authentication design for unresolved contracts.
