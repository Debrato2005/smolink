# Frontend agent instructions

**Owner:** Frontend instructions

## Scope

Agents may read the complete repository to understand product, API, security, backend, and deployment contracts. For frontend tasks, writes are restricted to `frontend/` unless a different scope is explicitly authorized.

Do not modify backend, database, infrastructure, deployment, root documentation, or unrelated files merely to make frontend work easier.

If frontend correctness depends on a change outside `frontend/`, document the dependency and blocker instead of silently crossing the ownership boundary.

The root [AGENTS.md](../AGENTS.md) and the [README testing policy](../README.md#testing-policy) still apply. Direct task instructions take precedence. Preserve dirty work. Do not reset, revert, stash, clean, commit, or push without explicit authorization.

## Startup order

1. Read the root instructions and this file.
2. Classify the task. Read only the relevant root API, architecture, security, or deployment owners.
3. Read the [entrypoint](README.md), [handoff](docs/HANDOFF.md), and exact task in the [queue](docs/BUILD_CHECKLIST.md).
4. Read the relevant stable owner in the [document index](docs/README.md).
5. Inspect current implementation and nearest tests. Check the executor and working directory before repository commands.

For Linux or WSL, use the Linux shell and workspace path directly. Do not wrap commands with Windows executors. Do not change sandbox permissions to repair ordinary repository commands. Report resource restrictions separately. Network downloads and loopback browser servers can require their own permission.

## Evidence and tools

Use current source/configuration/tests, observed behavior, root contracts, stable frontend owners, dated plans, and explicit uncertainty in that order. A target is not implementation evidence. A fixture is not live integration evidence.

Use `CURRENT`, `TARGET`, `PLANNED`, `BLOCKED`, and `DEFERRED` to qualify claims. Use the queue's status vocabulary for tasks. Claim a pass only after an observed run on the relevant source state.

Reach first for `rg`. Use focused Graphify queries when the root graph exists. Verify graph conclusions against source. Its legacy node IDs can collide. A root graph update writes outside this scope. Record it for separately authorized repository maintenance instead.

Read a relevant skill before use. Preserve `frontend/.agents/skills/` and `skills-lock.json`. Skills are agent guidance, not application dependencies. React guidance for Next.js does not apply to this Vite app.

## Implementation rules

Keep transport, adapters, and fixture selection behind [architecture boundaries](docs/FRONTEND_ARCHITECTURE.md). No presentation component calls `fetch`. No browser code connects to PostgreSQL or Redis. No fixture fallback follows a failed live request.

Important failures require visible feedback. Distinguish errors, confirmed empty results, unavailable features, and uncertain mutation outcomes. Never expose credentials, raw response payloads, or stack traces in feedback.

Use the [design owner](docs/DESIGN_SYSTEM.md) for tokens and component sources. Check rendered browser behavior for visual and interaction changes. Source intent does not prove acceptance.

## Completion procedure

1. Establish a meaningful failing check for a behavior change. Implement the smallest correct change.
2. Run the proportional gates in [quality](docs/TESTING_AND_QUALITY.md). Inspect keyboard, responsive, failure, and motion behavior when relevant.
3. Inspect the complete bounded diff, untracked files, and `git diff --check`.
4. Update stable documents only when stable truth changes. Update queue status only from acceptance evidence.
5. Write [HANDOFF.md](docs/HANDOFF.md) last. Record commands, results, limits, and one exact next task.

For cross-boundary blockers, record owner, exact files, current behavior, required change, compensation limits, and whether implementation or integration is blocked. Do not silently redefine backend contracts.
