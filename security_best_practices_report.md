# Smolink security and push review

Date: October 25, 2026, Asia/Kolkata.

## Decision and scope

**Full repository push clearance: BLOCKED. Production approval: NOT GIVEN.**

The final changes in this task affect frontend validation and this report.
Backend source, backend tests, Compose configuration, and the backend walkthrough
match their initial content. The pre-existing `backend/uv.lock` update remains.
Existing mobile layout, clipboard feedback, and frontend documentation work
also remain. No commit, push, package installation, or deployment occurred.

Frontend validation now rejects normalized destinations longer than 2048
characters and impossible local expiry dates. These checks improve frontend
feedback. The backend must independently enforce its input and account rules.

## Frontend fixes

- `frontend/src/lib/validation.ts:24` checks URL length after normalization.
  Percent encoding can expand a destination beyond the storage limit.
- `frontend/src/lib/validation.ts:38` compares the parsed expiry with the
  submitted local datetime. Invalid dates cannot silently become another day.
- `frontend/src/lib/validation.test.ts:4` covers the length boundary and Unicode
  expansion. Its second case covers impossible dates and a valid leap day.

Both regression cases failed before their fixes and now pass. The shared
validator serves the creation form and link details. No visual layout changed
in this task. Existing frontend layout changes need their browser checks.

## Open backend findings

The user excluded backend code changes. These findings remain open.

| ID | Severity | Finding and source | Impact and required work |
|---|---|---|---|
| SEC-01 | High | `backend/app/services/auth_service.py:391` loads the reset user without a row lock, then increments `auth_version` | Distinct concurrent resets can lose a session-version increment. Serialize account mutations and test independent PostgreSQL transactions |
| SEC-02 | Medium | `backend/app/services/auth_service.py:118` reads login state without a row lock before incrementing failures | Concurrent invalid logins can lose failures and delay lockout. Use an atomic counter or account lock |
| SEC-03 | Medium | `backend/app/services/auth_service.py:91`, `:128`, `:399` call synchronous Argon2 inside async services | Password work can delay unrelated requests. Use bounded worker threads and test event-loop progress |
| SEC-04 | Medium | `docs/docker-compose.yml:10`, `:23` publish development PostgreSQL and Redis without a host address | Other machines can reach them if host firewall rules permit. Bind development publication to loopback. Runtime exposure remains untested |
| SEC-05 | Low | `backend/app/main.py:5` uses default request-validation responses | Invalid authentication requests can echo credential input. Omit input and context from public validation errors |
| REL-01 | Reliability | `backend/app/schemas/url.py:12` accepts naive expiry. `backend/app/services/url_service.py:24` compares it with aware UTC | A naive expiry can produce HTTP 500. Require timezone-aware input |
| REL-02 | Reliability | `backend/app/schemas/url.py:10` allows destinations beyond the model's 2048-character limit | Direct API clients can bypass the new frontend check. Enforce the normalized limit in the backend |
| REL-03 | Reliability | `backend/tests/test_oidc.py:7` imports the missing `create_pkce_challenge` helper | Full backend test collection fails. Implement the RFC 7636 helper and run the suite. Google OIDC remains unfinished |

These are source findings with bounded reproductions, not production exploit
claims. The original audit used stale service snapshots to reproduce lost
updates. It did not establish PostgreSQL race behavior. Current ASGI regression
probes reproduced credential echo and invalid expiry behavior before final
backend restoration. No backend fix remains in this worktree.

PostgreSQL recommends consistent lock order to reduce deadlocks.
[PostgreSQL locking guide](https://www.postgresql.org/docs/16/explicit-locking.html).
AnyIO supports bounded worker threads for blocking work.
[AnyIO thread guide](https://anyio.readthedocs.io/en/stable/threads.html).
FastAPI supports custom request-validation handlers.
[FastAPI error guide](https://fastapi.tiangolo.com/tutorial/handling-errors/).

## Current verification

| Check | Result |
|---|---|
| Frontend validation, adapters, and runtime configuration | PASS: six tests |
| TypeScript and production build | PASS with Node 22.23.4 |
| Frontend lint, formatting, and document structure | PASS |
| Full frontend Vitest | BLOCKED: HTTP-server setup returned `listen EPERM`. The transport cases did not run |
| Chromium browser suite | BLOCKED: configured web server could not start |
| npm audit | BLOCKED: DNS lookup for `registry.npmjs.org` failed |
| Python lock audit | BLOCKED: DNS lookup for `api.osv.dev` failed |
| PostgreSQL and Redis | BLOCKED: no PostgreSQL response. Redis socket creation returned `EPERM` |
| Full backend collection | BLOCKED by the unchanged missing PKCE helper |
| Installed Python versions against current lock | Match |
| Frontend manifest against lock root | Match |
| Production fixture markers and public source maps | No matches or public source maps |
| Git integrity | PASS. Dangling local objects do not indicate branch corruption |
| Git whitespace | PASS |

The final snapshot does not retain the temporary backend implementation or its
regression tests. Test passes for that temporary state do not validate this
final backend. The private backend `.env` remains ignored.

The current history scan covers all 33 reachable commits and 1041 historical
blobs. It checks private keys, common provider-token patterns, literal JWTs,
and credential-bearing URLs. No checked token or private-key pattern matched.
Credential-URL candidates contain known synthetic or local-development values.
No historical blob exceeds 50 MiB. This bounded pattern scan does not prove
that no unknown secret exists. Generated output, dependencies, and ignored
local files remain outside the publication scan.

The frontend keeps credentials out of Web Storage, rejects unsafe URL schemes,
limits return navigation, and excludes fixture data from production bundles.
Source review found no arbitrary shell execution, unsafe HTML sink, or
user-controlled outbound fetch in application code. These observations do not
replace advisory audits or deployed security checks.

## Checks before publication

Use a host that permits local servers and advisory access. Use the supported
Node version and the existing dependency lockfile. Run from `frontend/`:

```bash
npm audit
npm test
npm run build
npm run test:e2e
SMOLINK_E2E_TARGET=production npm run test:e2e
```

Resolve actual failures before treating the frontend as verified. Full
repository clearance also requires the open backend findings, real
PostgreSQL/Redis tests, and Python advisory results. Production separately needs
proxy trust, TLS, session delivery, security headers, request-size limits,
email delivery, and recovery checks.

## Manual Git commands

After the frontend checks pass, these commands publish only the frontend
validation fix and report on a review branch. They do not approve production
or publish the existing mobile/confetti and backend lockfile changes. Inspect
any already staged work before this sequence.

```bash
cd /home/debrato/Projects/smolink
git switch -c codex/frontend-validation-hardening
git add -- frontend/src/lib/validation.ts frontend/src/lib/validation.test.ts \
  security_best_practices_report.md
git diff --cached --check
git diff --cached
git commit -m "fix(frontend): validate destination length and expiry dates"
git push -u origin codex/frontend-validation-hardening
```

Use a normal push. Do not force a push or rewrite history for these findings.
