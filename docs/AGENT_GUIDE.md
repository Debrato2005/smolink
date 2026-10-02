# Smolink Agent Guide

This guide defines agent workflow. The README defines architecture decisions.
The walkthrough describes implementation. The checklist records milestone
verification. Use each document for its stated purpose.

## Mission

Smolink is a backend-first URL shortener and an engineering learning project.
Build the smallest solution that meets the current milestone.

- Preserve the modular monolith unless evidence justifies a new boundary.
- Store durable data in PostgreSQL. Redis holds cache and ephemeral enforcement state.
- Preserve guest creation with no owner.
- Prefer explicit tools and interfaces with understood behavior.
- Record a replacement decision before reversing an architecture decision.

## Collaboration and authorization

Unless the user authorizes implementation, work as a read-only coding partner:

1. Inspect the relevant source and documentation.
2. Give the exact code, file location, and command for the requested step.
3. State the required walkthrough and checklist updates.
4. Stop after the requested step until the user authorizes continuation.

In that mode, do not edit files, run tests, or change repository state.
If the user asks for edits, tests, or documentation changes, complete the
authorized scope. User instructions for the task control that scope.
Keep replies concise and include enough detail to execute the step.

For authorized changes:

Inspect `git status` before editing. Preserve unrelated local work.

1. Read the affected behavior, tests, and architecture rules.
2. Make the smallest reversible change that satisfies the outcome.
3. Preserve module boundaries and unrelated working-tree changes.
4. Use only endpoints, persistence, dependencies, and abstractions required by the milestone.
5. Resolve requirements from evidence. Ask when an unresolved choice changes scope or a public contract.

Never use destructive Git commands to make the tree appear clean.

## Documentation order

Before changing behavior, read:

1. [README.md](../README.md): architecture, invariants, target API contracts, and roadmap.
2. [Backend build checklist](backend-build-checklist.md): current milestone and verification records.
3. [Codebase walkthrough](codebase-walkthrough.md): implementation and file responsibilities.
4. [Engineering Playbook](ENGINEERING_PLAYBOOK.md): reasoning and future concepts.

Also read the feature design or plan under `docs/superpowers/` when relevant.
Historical plans describe earlier work. Do not execute their obsolete examples
as current procedures. Use [development.md](development.md) for commands.

The README governs design decisions. Source and tests establish implemented
behavior. If those differ, document the gap without treating the target as
already implemented. Do not change code merely to make obsolete prose true.

## Skills and writing

Read the relevant skills in `.agents/skills/` before work. Use `fastapi` for
API conventions, `python-testing` for test behavior, and `graphify` for
relationships across files. Query an existing graph before broad source
searches. Check inferred edges against source.

The root [AGENTS.md](../AGENTS.md) defines the writing policy.
[Agent tooling](agent-tooling.md) explains skill usage, terminology, and
Graphify output handling. After source changes, run `graphify update .`.

## Development boundaries

| Layer | Responsibility |
|---|---|
| Route | HTTP concerns and transaction boundary |
| Schema | Request/response shape and validation |
| Service | Business policy and coordination through a shared session |
| Repository | SQL queries and persistence without commit |
| Utility | Reusable operations without a database or FastAPI dependency |

Some utilities manage local state or random values. Do not describe all
utilities as pure functions. Access another domain's data through its service
interface. Preserve `/api/v1` and established public response shapes.

Keep durable data in PostgreSQL. Planned redirect-cache failure must fall back
to PostgreSQL. Protected-write limiter failure must return `503`.
Use reviewed Alembic migrations for schema changes. Do not edit applied history
or manually change a deployed schema.

## Tests, errors, and dependencies

- Use the red-to-green workflow for behavior changes. Run a focused failing test before implementation.
- Test observable success and failure contracts. Avoid dependence on test order or leftover external state.
- Use unique data and fixture cleanup for fixed PostgreSQL/Redis state.
- Use real local PostgreSQL for constraint tests and Redis for Redis behavior.
- Use `-s` for the recorded pytest capture issue in this environment.
- Keep expected client failures distinct from unexpected `500` errors.
- Add dependencies only for current documented requirements.
- Keep commits focused and use imperative summaries when the user authorizes commits.

Do not add Kafka, workers, microservices, frontend, or deployment tooling to an
unrelated backend milestone.

## Documentation maintenance

- Update the walkthrough in the same change as source, tests, configuration, migration, Docker, CI, or frontend behavior.
- Update checked milestone status only after its required verification succeeds.
- Add dated progress records for completed, blocked, or deferred work.
- Update the README when decisions, invariants, target endpoints, or roadmap change.
- Synchronize dependent guides and link to one authoritative explanation.
- Preserve historical results and meaningful uncertainty.

## Decisions and completion

Choose among viable approaches in this order:

1. Correctness and documented invariants.
2. Simplicity within the current scope.
3. Maintainability and ownership boundaries.
4. Explicit behavior and testability.
5. Consistency with existing conventions.
6. Measured performance needs.

Surface choices that change an API, schema, durability, security, or operational
contract before implementation. Do not bundle speculative infrastructure or
unrelated formatting into a focused milestone.

Before completion:

1. Run relevant verification from `backend/`.
2. If the change affects shared behavior, run the full suite.
3. Review the diff for scope, secrets, generated files, and documentation drift.
4. Check that guides distinguish implemented behavior from targets.
5. Report changed areas, actual verification results, and remaining work.

Do not mark work complete from source inspection alone when tests are required.
Label user-reported results. Report failures and unavailable checks without
claiming a pass. Never commit secrets, `.env`, volumes, or local generated assets.
