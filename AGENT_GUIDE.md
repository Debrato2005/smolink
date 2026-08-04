# Smolink Agent Guide

This is the operational handbook for coding agents working in Smolink. It
orients work; it does not replace the repository's canonical documentation.

## 1. Mission

Smolink is a backend-first URL shortener built to demonstrate sound engineering
judgment, not maximum technology usage. Build the smallest production-minded
solution that the current milestone requires.

Non-negotiable principles:

- Preserve the modular-monolith architecture and evolve it only when evidence
  justifies a new boundary.
- PostgreSQL is the durable source of truth. Redis is cache-only for durable
  data and holds ephemeral rate-limit state.
- Guests must be able to create functional URLs without an owner.
- Prefer explicit, boring, well-understood solutions over speculative scale.
- Do not silently reverse a documented decision; propose and document a
  replacement decision first.

## 2. Agent Workflow

### Collaboration mode

Unless the user explicitly authorizes an action, work as a read-only coding
partner:

- First inspect the relevant repository files and canonical documentation.
- Give the exact code, file location, and command for the user to type and
  run; do not edit files, run tests, or otherwise change repository state.
- State which walkthrough and checklist updates the user should make, with the
  exact documentation text when useful.
- Stop after the requested step. Continue only when the user explicitly says
  to continue.
- Keep responses concise: lead with the next action, omit repeated context,
  and use only the detail needed to complete that step.

When the user explicitly asks the agent to edit, test, or update documentation,
perform only that authorized action and report the actual result.

1. Understand the affected behavior, its tests, and its canonical rules before
   editing.
2. Make the smallest reversible change that satisfies the requested outcome.
3. Preserve existing module and layer boundaries; do not refactor unrelated
   code while implementing a focused task.
4. Do not invent endpoints, persistence, dependencies, abstractions, or
   fallback behavior that the current milestone does not require.
5. Treat an uncertain requirement as a question to resolve, not a license to
   guess.
6. Preserve unrelated working-tree changes. Never use destructive Git commands
   to make the tree appear clean.

## 3. Documentation Order

Read these before changing behavior, in this order:

1. [README.md](README.md) — source of truth for architecture decisions,
   invariants, API contracts, and roadmap. Consult it for any design or API
   question; it wins if documents disagree.
2. [docs/backend-build-checklist.md](docs/backend-build-checklist.md) — current
   milestone, required scope, red-green steps, verification commands, and
   recorded progress. Consult it to determine what should happen next.
3. [docs/codebase-walkthrough.md](docs/codebase-walkthrough.md) — current
   implementation map and line-by-line explanations. Consult it before editing
   an unfamiliar file and update it when behavior changes.
4. [docs/ENGINEERING_PLAYBOOK.md](docs/ENGINEERING_PLAYBOOK.md) — the reasoning
   behind the architecture, backend practices, and future direction. Consult it
   when choosing between valid technical approaches or when a design decision
   needs context.

Also read a feature's design/specification or implementation plan under
`docs/superpowers/` when one exists. Repository-local `AGENTS.md` contains
additional development commands and conventions.

## 4. Development Rules

### Boundaries

- Routes handle HTTP concerns and transaction boundaries, not SQL or business
  rules.
- Schemas validate request/response shape.
- Services own business rules and coordination; they do not return HTTP
  responses or issue SQL directly.
- Repositories own SQLAlchemy queries and persistence operations; they do not
  decide business policy or commit transactions.
- Utilities are pure, reusable helpers with no database or FastAPI dependency.
- A module must not directly query another module's data store.

### Tests, errors, commits, and dependencies

- Follow red → green: write or adjust a focused failing test, implement the
  minimum behavior, then rerun focused and full verification.
- Keep tests isolated: do not rely on execution order or leftover database or
  Redis state; use unique data and clean fixed external-state keys in fixtures.
- Use real Compose PostgreSQL for database constraints and Redis for Redis
  behavior. Use `-s` with pytest in this environment.
- Keep API failures deliberate and consistent with the documented status and
  response contract. Do not turn expected client errors into `500`s.
- Keep commits focused on one milestone and use concise imperative messages.
- Add a dependency only when it solves a current documented requirement. Do not
  add Kafka, workers, microservices, or frontend/deployment tooling early.

## 5. Working Process

### Before coding

- Identify the requested milestone and read its relevant tests, source files,
  architecture rules, and any feature plan.
- Inspect `git status` and avoid overwriting unrelated local work.
- State assumptions or ask for direction when a choice would change scope or a
  public contract.

### During implementation

- Keep diffs narrow and preserve public response shapes and `/api/v1`.
- Put each concern in its proper layer.
- Make database changes through SQLAlchemy models and a reviewed Alembic
  migration; do not edit a deployed schema manually.
- Keep durable data in Postgres. Cache failure must not make durable data
  unavailable; protected-write rate-limit failure must fail closed as specified.

### Before finishing

- Run the relevant verification from `backend/`, then the full suite when the
  change affects shared behavior.
- Review the diff for accidental scope, secrets, generated artifacts, and
  documentation drift.
- Report commands and actual results. Never claim a test passed without running
  it or clearly labeling the result as user-reported.

## 6. Editing Rules

- Update `docs/codebase-walkthrough.md` whenever source, test, configuration,
  migration, Docker, CI, or frontend behavior changes.
- Update `docs/backend-build-checklist.md` only after its stated verification
  succeeds; add a concise progress-log entry for completed, blocked, or
  deferred work.
- Update `README.md` when an architecture decision, invariant, endpoint
  contract, or roadmap changes; then synchronize dependent documentation.
- Do not silently change architecture, API versioning, database ownership,
  failure policy, or a deferred feature's scope.

## 7. Decision Framework

When several implementations are viable, choose the option that best satisfies
this order:

1. Correctness and documented invariants.
2. Simplicity and the current milestone's scope.
3. Maintainability and clear ownership boundaries.
4. Explicit behavior and testability.
5. Consistency with existing code and documented conventions.
6. Measured performance needs—not hypothetical future scale.

If a trade-off changes an API, schema, durability, security, or operational
behavior, surface it before implementing it.

## 8. Anti-Patterns

Never:

- Treat Redis as authoritative for URLs or users.
- Require authentication for guest URL creation.
- Add a second alias-availability mechanism in v1.
- Conflate public `short_code` routes with owned-resource `id` routes.
- Put SQL in routes or business policy in repositories.
- Commit secrets, `.env` files, database volumes, or local generated assets.
- Modify applied migration history; create a new migration instead.
- Add speculative infrastructure, broad refactors, or unrelated formatting
  churn to a focused milestone.
- Mark checklist work complete without its required verification.
- Hide uncertainty, unverified results, or a conflict with canonical docs.

## 9. Completion Checklist

Before declaring work complete, confirm:

- [ ] The requested behavior matches README invariants and the active milestone.
- [ ] Tests cover the intended success and failure behavior.
- [ ] Focused and appropriate full verification ran successfully.
- [ ] The diff is minimal, layered correctly, and free of secrets/unrelated work.
- [ ] The walkthrough and checklist accurately reflect verified behavior.
- [ ] Any architecture or contract decision was explicitly documented.
- [ ] The handoff states changed files, verification results, and remaining work.
