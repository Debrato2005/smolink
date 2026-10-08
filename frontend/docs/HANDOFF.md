# Frontend handoff

**Owner:** Current frontend continuation checkpoint

Checkpoint: October 8, 2026 (Asia/Calcutta). The full-suite receipts cover the redesign and hover source. The logo follow-up has separate checks below.

## Current objective

Apply the supplied frontend redesign patch and finish its bounded frontend checks. Keep the neobrutalist measuring bench design and truthful backend availability. The user also requested a small hover lift for all boxed blocks.

Completed: patch application, archive removal, analytics text reflow, block hover behavior, Chromium checks, and documentation synchronization. Live accounts, Google OIDC, redirects, owner management, QR, and analytics still depend on the contracts below. This is not a release-ready product.

## What changed in this task

| Area              | Result                                                                                                                                                                                                                                                                                                                             |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Patch             | Initial `git status --short` returned no output. `git apply --check` and `git apply` passed from the repo root. No conflicts or three-way application occurred                                                                                                                                                                     |
| Archives          | Deleted `smolink-frontend-redesign.patch` and `smolink-frontend.zip` after application. The ZIP was never extracted                                                                                                                                                                                                                |
| Analytics         | Heading wraps inside its panel. Counts and dates wrap inside each column without fixed-height clipping. The strengthened 320px test first failed for all seven date labels, then passed after the CSS fix                                                                                                                          |
| Hover             | Boxed blocks lift by 2px and grow their hard shadow by 2px over 180ms. Landing cards, FAQ, account cards, notices, tickets, and workspace panels share this CSS behavior. No layout size changes. Reduced motion and touch-only pointers disable the lift. The new browser check failed before implementation and passed afterward |
| Formatting        | `.impeccable/` was already in `.prettierignore` after the patch. It remains excluded                                                                                                                                                                                                                                               |
| Docs and licenses | Synced design, architecture, workflows, queue, source ledger, quality, entrypoint, and QR notices. Both public QR notices match the installed licenses and the build copies byte for byte                                                                                                                                          |

## Verified checks

All tool commands started from `/home/debrato/Projects/smolink`. `npm --prefix frontend` runs npm scripts in `frontend/`. Node 22.23.2 came from `/home/debrato/.nvm/versions/node/v22.23.2/bin`. The default shell still selects Node 18, which does not meet the app's engine requirement.

| Check                                                                  | Observed result                                                                                                                                         |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `npm ci`                                                               | Passed. 227 packages installed from the lockfile. Cache: `frontend/.local/npm-cache`                                                                    |
| `npm run typecheck`                                                    | Passed, including the final production build's typecheck                                                                                                |
| `npm run lint`                                                         | Passed with zero warnings                                                                                                                               |
| `npm test`                                                             | 9 passed across 3 files. The first sandbox run passed 4 tests and skipped 5 after a loopback server failure. The loopback-authorized rerun passed all 9 |
| `npm run test:e2e -- --project=chromium`                               | 22 passed. Installed pinned Chromium 153.0.8010.12. Includes analytics text spacing, block hover geometry, reduced motion, and touch fallback           |
| `SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=chromium` | 4 passed against the final production build. API responses are injected. This does not prove backend integration                                        |
| `npm run build`                                                        | Passed. JavaScript 367.85 kB (gzip 116.30 kB). CSS 34.06 kB (gzip 7.10 kB)                                                                              |
| Production scan                                                        | Zero occurrences of `smolink.test`, `test-token`, and `fixtureLinks` in built JavaScript                                                                |
| `npm run docs:check`                                                   | Passed: 10 canonical owners, 16 unique tasks, local links and anchors                                                                                   |
| `npm run format:check`                                                 | Passed                                                                                                                                                  |
| `git diff --check`                                                     | Passed                                                                                                                                                  |
| Scope check                                                            | Tracked changes and new files are inside `frontend/`. No staged changes                                                                                 |

Normal sandbox execution blocked loopback listeners with `EPERM`. Network-enabled test and preview runs succeeded after the tool approval check. No ordinary Linux repository command used a Windows wrapper or changed sandbox permissions.

Browser commands used `PLAYWRIGHT_BROWSERS_PATH=/home/debrato/Projects/smolink/frontend/.local/browsers`. Temporary files used `TMPDIR=/home/debrato/Projects/smolink/frontend/.local/tmp`.

Visual review: analytics at 320, 390, 768, and 1440px, with normal and extra text spacing. Desktop card hover screenshots show the requested small lift. Receipts and captures are in ignored `.local/redesign-review/`. Firefox, WebKit, physical devices, screen readers, scanner decoding, and real-stack journeys did not run.

The new documentation prose scored 1.95 mechanical findings per 100 words in the STE linter. The handoff draft scored 1.25 findings per 100 words. These scores do not certify full ASD-STE100 compliance.

## Review server

The fixture development server runs at [http://127.0.0.1:3001](http://127.0.0.1:3001). Port 3000 was already occupied, so this task did not stop its listener. Command: `npm --prefix frontend run dev -- --port 3001`, with the Node path above. Development data is ephemeral. Production still disables missing backend features.

## Logo follow-up

Removed the frame and separate typed name at the user's request. The initial shared header/footer brand displayed the complete PNG with its original wordmark. Screenshots at 320, 390, and 1440px show no page overflow, border, or added shadow. The PNG request returned HTTP 200. Six focused Chromium navigation/reflow checks and the production build passed. The build includes the supplied PNG unchanged. Earlier full-suite receipts describe the redesign and hover changes before this logo follow-up.

Screenshots: `.local/redesign-review/logo/`. Docs prose lint: 0.92 findings per 100 words.

### Navbar crop follow-up

The user requested the symbol and original wordmark side by side in the navbar only. Two PNG crops now supply that layout. The footer keeps the complete artwork. The navbar uses smaller crops at widths of 900px or less.

The browser check first failed because the navbar contained one stacked image. After the crop change, the 768px check found horizontal overflow. Smaller crops resolved it. The final Chromium check passed at 320, 390, 768, and 1440px. Both images load beside each other with the same vertical center. The home link returns to the homepage. Visual review covered desktop and mobile captures.

Commands: `node .local/navbar-review/check.cjs`, `npm run lint`, `npm run build`, `npm run docs:check`, and `git diff --check`. These checks passed with the Node and browser paths above. The sandbox blocked loopback serving and Chromium startup. The authorized browser run used a local Vite server on port 3100. No dependency installation occurred. Firefox and WebKit did not run for this follow-up.

Screenshots and the browser check are in `.local/navbar-review/`. New documentation prose scored 0.75 findings per 100 words. Root Graphify output remains outside the frontend write scope.

The user then requested larger crops, less space at the left, and the actual logo in the browser tab. The navbar now uses larger crops and spans the viewport. Desktop symbol and wordmark widths are 60px and 160px. Horizontal padding is 24px, or 16px at widths of 900px or less. Smaller widths preserve the horizontal layout on narrow screens. The browser tab uses a transparent 64px PNG from the same symbol crop.

The size check first failed at the earlier 48px symbol width. Final Chromium checks passed at 320, 390, 768, 900, 1024, 1440, and 1920px without horizontal overflow. The favicon loads. The home link works. Build, lint, document checks, and whitespace checks passed. Visual review covered desktop and mobile captures. The final build contains JavaScript at 368.13 kB (gzip 116.43 kB) and CSS at 34.26 kB (gzip 7.22 kB). New size and favicon prose scored 0.00 mechanical findings per 100 words. The temporary port 3100 review server stopped after checks.

## Navbar social links

The user requested the supplied GitHub repository star count and X profile in the navbar. Boxed links now open both destinations in new tabs. Shields.io supplies the cached public star count. The GitHub link shows Star if the badge image fails. Social links move into the menu on phones. Desktop navigation collapses at 1150px. The narrow wordmark can shrink when increased text spacing needs more room.

The new browser test first failed because the links were absent. The first full Chromium run found overflow in the authenticated 320px header with increased text spacing. The wordmark shrink fixed that failure. The next full fixture run passed all 23 tests. A manual boundary check found overflow at 1051px. The final breakpoint change passed seven focused navbar, reflow, and axe checks. Visual review covered eight widths from 320px to 1920px, including both desktop links and the open phone menu. The real badge loaded and showed 2 stars.

Build, lint, formatting, document checks, and whitespace checks passed. Four production Chromium checks passed before the final breakpoint change. These tests inject API responses. Firefox and WebKit did not run. Captures and the review script are in `.local/social-review/`. Simple Icons supplies the GitHub and X paths under CC0. The license ships with the production build. No package installation occurred. Graph output remains outside the frontend write scope.

New social-link documentation prose scored 1.98 findings per 100 words. The temporary review server on port 3100 stopped after checks.

## Blockers and cross-boundary dependencies

The cross-boundary entries continue the supplied handoff. This task did not run backend or deployment tests. Source checks confirmed the missing PKCE helper and mounted route structure.

### ENV-02: Browser runtimes

This task used the installed pinned Chromium 153.0.8010.12, revision 1243. No substitute executable was selected. Firefox and WebKit did not run. Earlier download and WebKit host-library blockers were not rechecked. Cross-engine and physical-device verification remain open.

### CB-01: Lossless public ID transport

Owner: backend API/schema owners. Relevant files: `backend/app/schemas/url.py` and `backend/app/schemas/auth.py`. Current public IDs are JSON numbers. Required change: specify and implement lossless public IDs, preferably decimal strings, with matching tests and examples. JavaScript cannot restore precision after parsing an unsafe number. Frontend can preview public creation results without an ID, but live owner/account operations need the resolved transport contract. Independent fixture UI remains possible.

### CB-02: Browser session delivery and storage

Owner: backend authentication and security. Relevant files: `backend/app/api/v1/endpoints/auth.py`, `backend/app/schemas/auth.py`, `backend/app/services/auth_service.py`, and `docs/superpowers/specs/2026-08-01-authentication-authorization-design.md`. Current login/refresh return Bearer token JSON; no approved browser cookie/session delivery contract exists. Required decision: compare a same-origin server-managed session with in-memory browser credentials, including expiry, reload, CSRF where applicable, logout, and error handling. Frontend must not silently select persistent refresh-token storage. This blocks live session integration, not account form construction.

### CB-03: Rotation and browser concurrency

Owner: backend authentication with frontend session owner. Relevant files: `backend/app/services/auth_service.py` and `backend/app/repositories/auth_repository.py`. Current refresh rotation is single-use and replay revokes the token family. Required decision: define single-flight refresh and cross-tab ownership/binding before live integration. Multiple browser rotations can invalidate a legitimate session. Frontend cannot repair a server-revoked family or safely replay an uncertain mutation. Logout currently revokes refresh credentials while a valid access token can remain usable. This blocks live session integration.

### CB-04: Missing product endpoints

Owner: backend URL and analytics services. Relevant files: `backend/app/main.py`, `backend/app/api/v1/router.py`, and `backend/app/api/v1/endpoints/urls.py`. Current implementation lacks owner listing/update/delete, public redirect, QR, and analytics endpoints. Required change: implement explicit contracts, authorization, errors, and tests before live integration. Fixtures may support independent UI work, but cannot prove persistence, ownership enforcement, redirects, or reports.

### CB-05: Google OIDC and backend test collection

Owner: backend authentication. Relevant files: `backend/app/utils/oidc.py`, `backend/tests/test_oidc.py`, and mounted auth routes. Google start/callback routes are absent. The test module imports missing `create_pkce_challenge`; this is source-confirmed, not a fresh full-suite result. Required change: finish PKCE, browser binding, callback delivery, session handoff, and tests. Frontend cannot safely invent those security contracts. This blocks Google integration and an unconditional backend-suite claim; local fixture work remains independent.

### CB-06: Production origins and serving

Owner: deployment/infrastructure and backend. Relevant files: `backend/app/main.py`, `backend/.env.example`, and `docs/development.md`. Current backend has no CORS or SPA-serving policy. Required decision: establish TLS, production origins, API proxying or CORS, SPA deep-link fallback, security headers, and email public origin. A Vite development proxy is not production evidence. This blocks deployment integration.

### CB-07: Public short-code route precedence

Owner: backend URL service and deployment. Relevant files: `backend/app/utils/aliases.py`, `backend/app/services/url_service.py`, and `backend/app/main.py`. Current reservations do not cover every planned frontend path. Required decision: separate SPA/API paths from public codes and test collisions before publishing redirects. Frontend routing cannot enforce server-side uniqueness or request precedence. This blocks reliable deployed route integration.

### CB-08: Proxy identity and Snowflake generation

Owner: backend runtime/deployment. Relevant files: `backend/app/api/v1/dependencies/rate_limit.py`, `backend/app/utils/snowflake.py`, and the auth/URL endpoint modules. Current request identity uses the client host; trusted-proxy behavior is unresolved. Separate auth/URL generators use the same worker configuration, and timestamp bounds need backend review. Required change: define trusted proxy handling and verify generator identity/range guarantees. Frontend cannot repair rate-limit identity or database identifiers. These are backend/release dependencies, not reasons to stop fixture UI.

### CB-09: Root documentation and graph drift

Owner: repository documentation/tooling. Relevant files: root `README.md`, `docs/ENGINEERING_PLAYBOOK.md`, `docs/frontend-design-system.md`, `docs/backend-build-checklist.md`, `docs/codebase-walkthrough.md`, `docs/AGENT_GUIDE.md`, and `graphify-out/`. Root guidance still describes planned frontend work and older design ownership. Focused Graphify queries worked but warned about legacy node IDs. Required separately authorized maintenance: reconcile root guidance and refresh the graph after this frontend work. This task must not write those paths. Current source and frontend owners govern the implemented foundation within this scope.

### CB-10: Email delivery recovery contract

Owner: backend authentication/email services. Relevant files: `backend/app/api/v1/endpoints/auth.py`, `backend/app/services/email_service.py`, and `backend/app/services/auth_service.py`. Registration can commit before email delivery fails. Forgot-password and resend return empty 202 acceptance without guaranteeing delivery. Required follow-up: define provider-outage and resend recovery behavior before live forms promise an outcome. Frontend cannot undo a committed account or infer delivery from acceptance. This affects live recovery integration; form and fixture work can proceed.

### CB-09 note: root design reconciliation

`--sky-surface` is a frontend token added at the user's request. Root `docs/frontend-design-system.md` does not list it. Reconcile the root file under separate authorization. Root `graphify-out/graph.json` exists but lacks the frontend analytics modules. The graph and root documentation remain outside this task's write scope.

## Exact next task

Run the fixture and production suites in Firefox and WebKit on a host with the pinned runtimes and required host libraries. Keep the receipts separate from Chromium. Then complete FE-007 with a real backend guest-creation journey.

From `frontend/`, with the supported Node runtime and provisioned browsers:

```bash
npm run test:e2e -- --project=firefox --project=webkit
npm run build
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=firefox --project=webkit
```

Review the outlined hero word, ticket `cqi` sizing and notches, block hover, reduced motion, and analytics text spacing.

## Scope protections

All file writes are inside `frontend/`. No `git add`, commit, push, stash, reset, clean, or checkout command ran. No conflict resolution occurred. Root documentation, backend code, and graph output remain unchanged. Preserve `.agents/skills/` and `skills-lock.json`. `.impeccable/` remains development-only and excluded from Prettier.
