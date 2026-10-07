# Frontend handoff

**Owner:** Current frontend continuation checkpoint

Checkpoint: October 7, 2026. Implementation and browser receipts below come from October 6 UTC. This checkpoint replaces the foundation-only handoff.

## Current objective

Continue the complete Smolink frontend and its browser refinement loop. **The product is unfinished and is not ready for release.**

The frontend now includes the landing page, URL creation, results, QR preview, account forms, and a fixture workspace. Build, typecheck, lint, and nine existing tests passed. The latest fixture browser run reported **23 passed and nine failed**. Production browser artifacts also record two failures. Final visual acceptance and documentation synchronization remain incomplete.

The user's latest instruction was to generate this handoff. This continuation wrote the handoff and inspected existing evidence. It did not fix application code or rerun browsers.

Retain these user constraints:

- Write only inside `frontend/`. Preserve existing dirty work, backend contracts, and the adapter boundary.
- Use Neobrutalism primitives, Bauhaus composition, and restrained Pop Art accents. Keep public pages expressive and the workspace controlled.
- Take actual browser screenshots, inspect them, and fix observed defects. Work quickly, but do not replace evidence with completion claims.
- Keep Ponytail active: reuse native controls, CSS, existing components, and installed dependencies. Avoid speculative abstractions and extra motion libraries.
- Label fixtures and unavailable capabilities. Never use fake data after a failed production request.

## Current implementation

| Area          | Files under `frontend/`                                                        | Current behavior and limits                                                                                                                                        |
| ------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Public shell  | `src/app/App.tsx`, `src/routes/Home.tsx`                                       | Responsive navigation, footer, hero, features, steps, FAQ, and creation panel. Explicit fixture/live banner.                                                       |
| Creation      | `src/features/shorten/ShortenPreview.tsx`, `src/lib/validation.ts`             | Destination, optional alias, optional expiry, adjacent validation, pending state, conflicts, limits, and uncertain mutation feedback.                              |
| Results       | `src/features/shorten/LinkActions.tsx`                                         | Awaited clipboard confirmation, manual copy after denial, QR dialog, and PNG download. Live QR remains unavailable.                                                |
| Accounts      | `src/features/auth/AuthPage.tsx`                                               | Sign in, sign up, verification, resend, recovery, reset, missing-token, locked, and unverified states. Fixture actions only. Live forms remain explicitly blocked. |
| Workspace     | `src/features/workspace/WorkspaceLayout.tsx`, `Dashboard.tsx`                  | Fixture identity guard, sign out, overview, URL list, search, filter, sort, and six-row pagination. Query parameters hold list controls.                           |
| Management    | `src/features/workspace/LinkDetail.tsx`                                        | Fixture destination/expiry edits, enabled state, copy/QR, success feedback, and destructive confirmation.                                                          |
| Analytics     | `src/features/workspace/Analytics.tsx`                                         | Seven/30 sample-day reports, chart, exact daily table, referrers, devices, UTC dates, freshness, and confirmed zero-data states. Keyboard defect remains.          |
| Shared UI     | `src/components/ui/`                                                           | Base UI buttons/dialog, labeled fields, SVG icons, loading, and error feedback. Native select, checkbox, date-time input, details, and tables.                     |
| API boundary  | `src/lib/api/contracts.ts`, `gateway.ts`, `live.ts`, `fixtures.ts`             | `ProductGateway` extends the existing creation boundary. Live guest creation retains the HTTP adapter. Other live operations fail explicitly.                      |
| Runtime/state | `src/main.tsx`, `src/lib/useResource.ts`, `src/app/router/NavigationFocus.tsx` | Email fragment capture/removal, cancellable reads, navigation focus, and anchor scrolling. Review token cleanup through Strict Mode before live auth integration.  |
| Design        | `src/styles/globals.css`, `tokens.css`                                         | Flat fills, black borders, hard shadows, geometric artwork, responsive rules, and reduced-motion rules. New styles still need token consolidation and formatting.  |

React 19.3.0, Vite 8.3.2, React Router 8.4.0, TypeScript 6.0.3, and Base UI 1.8.0 remain selected. The new direct dependency is `qrcode` 1.5.4. Its types are `@types/qrcode` 1.5.6. Both use the MIT license. The lockfile changed during installation. The dependency notice and source ledger still need updates.

### Fixture versus live behavior

`fixtures.ts` contains 12 initial sample links and an in-memory mutation store. Reload resets changes. Sample short URLs use `.invalid` and do not redirect. The fixture date is illustrative, based on October 6, 2026. Generated QR images encode those sample URLs correctly but do not create redirect infrastructure.

Use `/login` and **Explore demo workspace** to enter the fixture workspace. The development selector exposes `normal`, `empty`, `error`, `limited`, `locked`, `unverified`, and `expired` scenarios. Account actions simulate results without storing passwords. `wrong@example.com` simulates invalid credentials. Verification/reset accepts `demo-token`, available through **Load demo email link**.

Live guest requests use `/api/v1/urls`. The frontend does not implement a live account session or store bearer/refresh credentials. Google start/callback remains absent. Owner list/edit/delete, redirect, and analytics endpoints remain backend dependencies. Successful production-response tests inject HTTP responses and do not prove a real backend journey.

Unsafe numeric public IDs still become `linkId: null`. Never infer a precise ID or ownership from a public short code. Alias normalization and validation follow backend rules. Expiry converts browser-local input into a future UTC ISO timestamp.

## Verified checks

These receipts apply to the implementation checkpoint, not a completed release. The old foundation's green results do not cover the expanded product.

| Check                               | Observed result                                                                                                                                                                               |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Initial focused browser checks      | Two expected failures established missing alias and workspace behavior. After implementation, both Chromium checks passed.                                                                    |
| `npm run typecheck`                 | Passed after implementation corrections.                                                                                                                                                      |
| `npm run lint`                      | Passed after removal of synchronous state updates from the resource effect.                                                                                                                   |
| `npm test`                          | Nine tests passed in three files. Receipt: October 6, 06:56 UTC. HTTP tests use native Fetch and loopback HTTP.                                                                               |
| `npm run build`                     | Passed, 268 modules. JavaScript 371.15 kB, gzip 116.58 kB. CSS 32.65 kB, gzip 7.25 kB.                                                                                                        |
| Earlier expanded browser run        | 24 passed, two failed. The failures used an ambiguous status locator. The test then selected the save-confirmation status.                                                                    |
| Latest Chromium/Firefox fixture run | 23 passed, nine failed out of 32. Five analytics keyboard failures, one Chromium 320 px overflow, and three Chromium trace-close errors.                                                      |
| Production browser run              | `.last-run.json` records two failures. Both traces stop at the broad `getByText('Demo mode')` assertion. The final process output was not recovered. No aggregate production pass is claimed. |
| WebKit                              | Browser launch blocked by missing host libraries. No WebKit product-flow pass.                                                                                                                |
| Screenshot capture                  | Home, login, dashboard, detail, and analytics captured at 1440 and 390 px. Capture script reported no horizontal overflow or console/page errors at those widths.                             |
| Handoff scope check                 | All 87 non-frontend baseline files match their hashes. No new non-frontend tracked or unignored file paths appeared.                                                                          |

The final production fixture-rejection build and bundle scan were not repeated after expansion. Full formatting and documentation gates were not repeated during implementation. Physical-device checks, manual screen-reader checks, performance measurements, and real-stack flows remain unverified.

### Exact failing evidence

1. **Analytics keyboard access:** five traces report serious `scrollable-region-focusable` violations on `.daily-table-wrap`. Its scrollable content lacks keyboard focus. The planned `tabIndex={0}` and named region patch did not execute. Current `Analytics.tsx` still contains the unfocusable wrapper.
2. **320 px Chromium overflow:** `product.spec.ts:171` fails the document-width assertion on the detail screen. This happens before analytics. Inspect the real viewport and overflowing elements instead of hiding page overflow.
3. **Three Chromium artifact failures:** workspace management, account forms, and filter/edit/outage checks report `browserContext.close: ENOENT` for missing trace files. The main suite and a separate WebKit invocation shared `test-results/fixture` concurrently. That collision is a likely cause, not a confirmed diagnosis. Rerun separately before changing product behavior.
4. **Production locator failure:** `production.spec.ts:19` expects no text containing “Demo mode.” The snapshot shows **Live API mode**. The FAQ includes “In demo mode,” which the broad locator also matches. Narrow the assertion to the mode banner and separately verify transport and bundle exclusion.

Failure snapshots and trace ZIPs remain in `test-results/fixture/` and `test-results/production/`. The `.last-run.json` files report failure. Test artifacts are ignored and can disappear on a later run. Preserve useful receipts before rerunning.

### Screenshots and remaining visual checks

The capture script is `.local/capture.mjs`. Saved files include:

| Screen       | Desktop                                 | Mobile                                |
| ------------ | --------------------------------------- | ------------------------------------- |
| Hero         | [1440 px](../.local/hero-1440.png)      | [390 px](../.local/hero-390.png)      |
| Full landing | [1440 px](../.local/home-1440.png)      | [390 px](../.local/home-390.png)      |
| Sign in      | [1440 px](../.local/login-1440.png)     | [390 px](../.local/login-390.png)     |
| Dashboard    | [1440 px](../.local/dashboard-1440.png) | [390 px](../.local/dashboard-390.png) |
| Link details | [1440 px](../.local/detail-1440.png)    | [390 px](../.local/detail-390.png)    |
| Analytics    | [1440 px](../.local/analytics-1440.png) | [390 px](../.local/analytics-390.png) |

The agent visually inspected the desktop hero, mobile landing, desktop dashboard/sign-in, and mobile analytics. The captures exposed a desktop hamburger, duplicate active workspace links, joined analytics caption text, and an opaque auth ornament.

Subsequent source edits addressed navigation, active links, the ornament, small text, and mobile hero density. They were not recaptured. The caption uses a `br::after` spacing attempt that still needs browser inspection. Prefer explicit text spacing if that attempt fails. These images are earlier evidence, not final acceptance images.

## Research and tool decisions

The agent used the installed frontend design, React, Playwright, Graphify, ASD-STE100, Ponytail, and Lean Build guidance. Project rules take precedence over generic skill recipes. No extra state, form, chart, GSAP, or Lenis dependency was added.

Sources inspected during implementation still need entries in [SOURCE_LEDGER.md](SOURCE_LEDGER.md):

| Source                                                                                                                             | Use                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| [neobrutalism.dev dialog](https://www.neobrutalism.dev/docs/dialog), [Base UI dialog](https://base-ui.com/react/components/dialog) | Primitive behavior and installed Base UI composition. Registry downloads failed, so installed types and docs guided the wrapper. |
| [Neubrutalism.com](https://neubrutalism.com/)                                                                                      | Flat fills, borders, restrained hard-shadow language.                                                                            |
| [MoMA Herbert Bayer reference](https://www.moma.org/collection/works/5101)                                                         | Bauhaus hierarchy and geometric composition.                                                                                     |
| [Dribbble URL-shortener dashboard](https://dribbble.com/shots/26997319-URL-Shortener-Dashboard-UI)                                 | Product density and hierarchy reference. No layout or branding copied.                                                           |
| [Linear features](https://linear.app/features), [Dub link builder](https://dub.co/blog/new-link-builder)                           | Product task priority and link-action visibility. No session-storage pattern adopted.                                            |
| [node-qrcode](https://github.com/soldair/node-qrcode)                                                                              | Actual client-side QR generation in the fixture boundary.                                                                        |
| [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md)                 | Interaction and accessibility review guidance.                                                                                   |

The Awwwards Flowfest page timed out. Search results did not establish meaningful visual inspection. Awwwards research remains incomplete.

Impeccable's context loader failed because it could not create its engine directory outside this scope. The agent read existing project context directly. No successful engine execution is claimed. Graphify queries worked with legacy-ID warnings. Root graph updates remain outside scope.

## Blockers and cross-boundary dependencies

### ENV-02: WebKit host libraries

Pinned Chromium, Firefox, and WebKit runtimes downloaded under `.local/browsers/`. WebKit reports missing `libevent-2.1-7t64` and `libgstreamer-plugins-bad1.0-0`. Host provisioning belongs outside this frontend write scope. It blocks local WebKit verification only. Use a correctly provisioned host for the configured project; do not report a configured engine as tested.

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

### ENV-03: Approval review unavailable

Automatic approval review rejected the final browser rerun because the workspace owner's spend cap prevented review. The action did not execute. This was a review failure, not a finding that the action was unsafe.

The rejected call bundled the analytics focus patch with the browser rerun. Neither action ran. Do not bypass review. Resume restricted browser execution only after the approval service works or the user supplies an approved path. Ordinary reads and this frontend documentation update remained available.

## Unfinished work

The stable frontend owners and queue still mostly describe the earlier foundation. In particular, FE-007/008/009/011/012/013 remain `TODO` despite implementation work. Their acceptance remains incomplete. Do not mark them `DONE_VERIFIED` from screenshots or isolated passes.

Update [FRONTEND_ARCHITECTURE.md](FRONTEND_ARCHITECTURE.md) for `ProductGateway`, fixture sessions, resource reads, and email-token lifetime. Update [WORKFLOW.md](WORKFLOW.md) for actual routes and live/fixture availability. Reconcile [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md), [TESTING_AND_QUALITY.md](TESTING_AND_QUALITY.md), [BUILD_CHECKLIST.md](BUILD_CHECKLIST.md), and [README.md](../README.md) with observed implementation.

Record `qrcode` and its types in the source ledger and third-party notices. Preserve the required license text under `public/licenses/`. Review the lockfile diff. Remove or update the unused foundation route map in `src/app/router/route-map.ts`. Format the new TSX/CSS and consolidate repeated values into the existing token system.

## Exact next task

**Fix the analytics table's keyboard access in `src/features/workspace/Analytics.tsx`.** Keep the existing scroll wrapper, add keyboard focus and an accessible region name, and use the existing failing browser check. The rejected patch did not apply.

Then continue in this order:

1. Fix the observed 320 px detail overflow and narrow the production mode assertion.
2. Rerun browser invocations separately and inspect fresh screenshots after each visual correction.
3. Complete token/format cleanup, dependency notices, and source-ledger entries.
4. Synchronize the stable owners and task queue with actual acceptance evidence.
5. Run the relevant final gates, compare scope hashes, and rewrite this handoff last.

### Commands and runtime

Run from `frontend/` under Linux Bash. System Node 18 is too old. Use the installed Node 22.23.2:

```bash
export PATH=/home/debrato/.nvm/versions/node/v22.23.2/bin:$PATH
export TMPDIR="$PWD/.local"
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/browsers"
npm run dev -- --port 3100
```

Normal development uses port 3000. Fixture browser tests use 3100. Production preview uses 4173. Check whether a server exists before starting another. Old executor process IDs are not reliable continuation handles. Set `SMOLINK_E2E_REUSE=1` only for a verified matching server.

Once browser execution is available, run these separately:

```bash
SMOLINK_E2E_REUSE=1 npx playwright test product.spec.ts --project=chromium -g 'workspace and analytics'
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --project=firefox
npm run build
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=chromium --project=firefox
```

Do not run two Playwright invocations against the same output directory concurrently. Preserve traces before a rerun. A fixture pass does not resolve live contract blockers.

Final gates also include `typecheck`, `lint`, `format:check`, `test`, `docs:check`, fixture-build rejection, production bundle inspection, and bounded diff review. Do not install host libraries or edit root files under this authorization.

## Scope protections

The initial checkout already contained dirty root documentation and an untracked frontend foundation. No commit, push, reset, stash, clean, or worktree operation occurred.

Application changes, dependencies, caches, browser runtimes, screenshots, test artifacts, and this handoff stay under `frontend/`. The product baseline is `.local/product-outside-baseline.json`. The earlier foundation baseline remains `.local/outside-baseline.json`.

The handoff comparison found 87 unchanged non-frontend baseline files and no new non-frontend tracked or unignored file paths. This check does not cover every ignored tool cache. Preserve installed skills and `skills-lock.json`. Root documentation and Graphify updates require separate authorization.
