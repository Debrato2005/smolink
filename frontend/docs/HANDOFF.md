# Frontend handoff

**Owner:** Current frontend continuation checkpoint

Checkpoint: October 9, 2026 (Asia/Calcutta). The current control and hover receipts are below. Earlier redesign and logo receipts remain historical.

## Current objective

The current objective is to refine the reference tickets, enlarge the left hero, and add the requested controls. This includes calendar time entry, contact drafts, dropdowns, sidebar collapse, skeleton loading, and adjusted hover behavior. Earlier redesign receipts below remain historical. Live product acceptance still has the listed contract blockers.

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

## Split hero follow-up

The user requested a 40/60 desktop layout to keep the newest short link visible without a manual scroll. The headline and description now sit on the left. The form and newest result share the right panel. At widths of 900px or less, the columns stack.

The result appears above the form. Its URL receives focus and selects its text. Focus preserves the scroll position when the result is visible. The browser brings an offscreen result into view. The test first failed against the stacked layout. The first focus method moved the desktop scroll position by 74px. Focus with `preventScroll` resolved that movement.

The final Chromium fixture suite passed all 24 tests. The focused test checked 1366 × 768 and 1440 × 900 with no desktop scrolling. It also checked result visibility at 390 × 844. Four production Chromium checks passed with injected API responses. Build, lint, formatting, document checks, and whitespace checks passed. Visual review covered desktop idle and result states, plus the mobile layout. Firefox and WebKit did not run. No backend or root graph files changed.

Result captures: `test-results/shortener-split-1366.png` and `test-results/shortener-split-1440.png`. Idle captures: `test-results/chromium-1440.png` and `test-results/chromium-390.png`. Build sizes: JavaScript 370.35 kB (gzip 117.50 kB), CSS 34.82 kB (gzip 7.34 kB). New stable prose scored 0.00 findings per 100 words. The handoff draft scored 1.12 findings per 100 words.

## Centered panel follow-up

The user requested output below input, with the panel centered and the yellow strip at the bottom on initial load. The result now follows the form. The hero and strip share an intro that fills the remaining desktop viewport. The card grows upward and downward around its center when the content fits. Taller content extends the page. Mobile keeps the stacked layout and brings the result into view when needed.

The browser check first failed because the strip ended 219px above the viewport bottom. After the change, the check passed at 1366 × 768 and 1440 × 900. It checks the strip position, center alignment, output order, growth in both directions, and result visibility without desktop scrolling.

The final Chromium fixture suite passed all 24 tests. Four production Chromium checks passed with injected API responses. Build, lint, formatting, document checks, and whitespace checks passed. Visual review covered idle and result states. Firefox and WebKit did not run. Backend and root graph files remain outside the write scope.

Idle captures: `test-results/shortener-centered-idle-1366.png` and `test-results/shortener-centered-idle-1440.png`. Result captures: `test-results/shortener-split-1366.png` and `test-results/shortener-split-1440.png`. Build sizes: JavaScript 370.40 kB (gzip 117.50 kB), CSS 34.99 kB (gzip 7.37 kB). New prose scored 0.46 findings per 100 words.

## Hero copy follow-up

The user requested catchier copy and a stronger visual treatment for the left hero block. The headline now reads Big ideas. Smol links. An ink label, yellow headline highlight, and long-to-short URL illustration add emphasis. The existing split layout, centered panel, and result order remain intact.

Six focused Chromium fixture checks passed. They cover reflow and axe at five widths from 320px to 1440px, plus panel alignment and result visibility. Visual review covered desktop and phone captures. Build, lint, formatting, document checks, and whitespace checks passed. These checks do not prove live backend integration. Firefox and WebKit did not run.

Captures: `test-results/chromium-1440.png` and `test-results/chromium-390.png`. No dependencies were added. Root graph output remains outside the frontend write scope.

New documentation prose scored 1.12 findings per 100 words.

## Reference-based hero follow-up

The user rejected the first hero treatment and supplied two visual references. The hero now reads Long links? Smol it. It uses heavier type, a paper label, yellow emphasis, sticker artwork, and a yellow Shorten button. Rounded corners follow the supplied reference within the hero. The split layout, centered panel, and output below input remain intact.

Six focused Chromium fixture checks passed. They cover reflow and axe at five widths, plus panel alignment, result order, and result visibility. A browser review also checked the loaded font and artwork, console errors, and a wide desktop viewport. Build, lint, formatting, document checks, and whitespace checks passed. These checks do not prove live backend integration. Firefox and WebKit did not run.

The visual QA report is design-qa.md. Comparison receipts are in .local/hero-reference-review/. The preview remains open at http://127.0.0.1:3100/. No dependencies were installed. Root graph output remains outside the frontend write scope.

Commands: `npm run lint`, `npm run build`, `npm run docs:check`, `git diff --check`, and `SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep "desktop shortener|home reflows"`. The browser checks used Node 22.23.2 and the installed pinned Chromium runtime. New stable prose scored 1.03 findings per 100 words. The visual QA draft scored 0.67.

## Hero artwork and surface follow-up

The user requested longer sticker text, a blue shape behind the form, and a boxed headline. Two supplied references govern the box and blue surface. The blue illustration is decorative and hidden from assistive technology. The hero uses a separate surface token. Other page surfaces keep their existing token.

Six focused Chromium fixture checks passed after the final change. They cover responsive reflow, axe, panel alignment, output order, and result visibility. Visual review covered desktop and phone renders. Build, lint, formatting, document checks, and whitespace checks passed. These checks do not prove live backend integration. Firefox and WebKit did not run.

Artwork paths: public/hero-link-stickers.png and public/hero-blue-backdrop.png. The assets use transparent output from the built-in image tool. No fallback CLI or package installation ran. The exact prompts and visual comparison receipts are in .local/hero-reference-review/. The preview remains available at http://127.0.0.1:3100/. Root graph output remains outside the frontend write scope.

Commands: `npm run lint`, `npm run build`, `npm run docs:check`, `git diff --check`, and `SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep "desktop shortener|home reflows"`. New prose scored 0.00 findings per 100 words.

## Hero component conversion — October 8, 2026

The user requested real components and research into ready-made alternatives. The URL labels now remain selectable and editable in source. The full grid, headline box, pale blue surface, 40/60 split, and centered form remain in place. The newest result still appears below the input.

`src/components/HeroArtwork.tsx` supplies real text with CSS stickers and decorative inline SVG. Both unused hero PNG files were removed from public assets. Earlier prompts and comparison receipts remain historical evidence. Current captures and browser checks are in `.local/hero-components/`. The source ledger records the reviewed cards, badges, SVG stars, and CSS patterns. No package or CLI installation ran.

Checks from `frontend/`, with Node 22.23.2 and the provisioned Chromium runtime:

```bash
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'desktop shortener|home reflows'
npm run build
npm run lint
npm run format:check
npm run docs:check
git diff --check
```

Six existing Chromium fixture checks passed, including responsive reflow and centered panel expansion. Build, TypeScript, lint, formatting, document structure, and whitespace checks passed. Browser checks at 1440, 390, and 320px confirmed selectable text, the original full grid, no raster hero requests, and no page errors. The prose draft lint score was 2.03 findings per 100 words. Firefox, WebKit, and live backend checks did not run for this change. Root graph maintenance remains outside the frontend write scope. The preview is http://127.0.0.1:3100/.

## Blue oval layering — October 8, 2026

The user requested the blue component above the grid and closer to the new reference. The SVG now uses a broad rotated ellipse with smaller ink rays near its upper-right edge. Its fill is opaque. The grid, blue backdrop, and hero content occupy separate layers in that order. The result still appears below the input and expands around the panel center.

Current viewport captures and layer checks are in `.local/hero-blue-layer/`. Checks cover 1440 by 900, 1366 by 768, and 390 by 844 viewports. The grid keeps its original spacing and alignment. Six focused Chromium fixture checks passed. Build, lint, formatting, document structure, and whitespace checks passed. Firefox, WebKit, and live backend checks did not run for this change. Root graph maintenance remains outside the frontend write scope. Prose draft lint: 0.57 findings per 100 words.

Commands from `frontend/`, with Node 22.23.2 and the provisioned Chromium runtime:

```bash
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'desktop shortener|home reflows'
npm run build
npm run lint
npm run format:check
npm run docs:check
git diff --check
```

## Ticket comparison and home reload — October 8, 2026

Three candidates were rendered at desktop and phone sizes: flat tickets, rounded stickers, and a spaced hybrid. The spaced hybrid was selected. It keeps the ticket edges and labels, with a curved arrow and gentle tilt. Its wider gap separates the arrow and scissors from the text. Matching ticket height and center alignment make the pair easier to compare. Desktop spacing moves the illustration left without clipping it. The long URL has no strike-through.

The enlarged blue oval is centered on the form panel. Its diagonal follows opposite panel corners. It stays above the grid and below the form. Desktop spacing keeps the oval clear of the ticket illustration. The grid keeps its original spacing and alignment. On phones, the backdrop stays behind the stacked form.

Home reload starts at the top of the hero. Before rendering, `main.tsx` detects a reload on the root path, selects manual scroll restoration, removes the section fragment, and resets scrolling. Query parameters stay in place. Normal section links and initial deep links still scroll to their targets. Other routes keep their existing startup behavior.

The reload regression failed before the fix because the Questions fragment returned to that section. Eight focused Chromium fixture checks now pass. Four existing Chromium production checks also pass with injected API responses. These checks do not prove live backend integration. The final browser checks cover seven viewport sizes from 320 to 1440 pixels. They confirm text fit, matching ticket height and center alignment, no strike-through, centered oval geometry, desktop clearance, and no page overflow. Build, lint, formatting, document structure, and whitespace checks passed. Firefox and WebKit did not run for this change. Root graph maintenance stays outside the frontend write scope.

Commands from `frontend/`, with Node 22.23.2 and the provisioned Chromium runtime:

```bash
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'home reload|desktop shortener|home reflows|keyboard, navigation'
npm run build
npm run lint
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=chromium
npm run format:check
npm run docs:check
git diff --check
```

Comparison boards, candidate captures, scripts, and final captures are in `.local/hero-three-options/`. `variants.json` records the trial CSS and SVG paths. `final-checks.json` records the final geometry checks. [design-qa.md](../design-qa.md) records the selection. Prose draft lint: 1.99 findings per 100 words. The local fixture preview was restarted on http://127.0.0.1:3100/.

The earlier approval reviewer usage limit prevented one browser check. The later authorized browser calls succeeded. Impeccable context loading remains unavailable because its engine is not installed. Existing product/design owners and the written skill guidance supplied context. No engine or package installation ran.

## Labels inside tickets and expanding oval — October 8, 2026

The user approved the reference with labels inside the tickets and a straight arrow. The current layout follows that reference. Both desktop columns are wider and sit farther left. The panel still expands upward and downward, with the result below the input. The blue oval grows with the panel. Ink marks stay at the panel corner, clear of the ticket text. The original grid keeps its spacing and alignment.

The new oval regression failed before the fix and passed after the fix. Eight focused Chromium fixture checks pass. Four Chromium production checks pass with injected API responses. Build, lint, formatting, document structure, and whitespace checks passed. These checks do not prove live backend integration. Firefox and WebKit remain open.

Captures and geometry checks are in `.local/hero-ticket-inside/`. The capture script checks seven viewport sizes in idle and result states. It confirms text fit, equal ticket height, no page overflow, the original grid, oval clearance, and no desktop scrolling. The input focus animation must finish before the capture runner clicks. Otherwise, browser automation can scroll during that animation.

Commands from `frontend/`, with Node 22.23.2 and the provisioned Chromium runtime:

```bash
node .local/hero-ticket-inside/check.mjs
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'home reload|desktop shortener|home reflows|keyboard, navigation'
npm run build
npm run lint
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=chromium
npm run format:check
npm run docs:check
git diff --check
```

Prose draft lint: 0.44 findings per 100 words. The exact next task below stays unchanged. Root graph maintenance remains outside the frontend write scope.

## Rounded sticker selection — October 8, 2026

The user selected rounded stickers. They now have equal width and height, matching tilt, and hard shadows. A curved arrow connects them. Desktop spacing moves the pair 16px left. The oval still grows with the result panel.

Eight focused Chromium fixture checks, build, lint, formatting, and document checks pass. Seven viewport captures confirm text fit and no clipping. Firefox, WebKit, and live backend checks remain open.

The existing commands and `.local/hero-ticket-inside/` captures above apply to this revision. Prose draft lint: zero findings. The exact next task below stays unchanged.

## Larger stickers and corner rays — October 8, 2026

Both rounded stickers are taller, with larger text and matching dimensions. The pair sits centered beneath the hero copy. A straight arrow has matching arrowhead sides and sits halfway between the stickers. Ink rays attach to the yellow sticker's top-right corner and follow its tilt. The sticker group stays above the blue oval.

Seven viewport checks cover idle and result states. All eight focused Chromium fixture checks pass. Build, lint, formatting, and document checks pass. Firefox, WebKit, and live backend checks remain open. The existing commands above apply to this revision. Current captures stay in `.local/hero-ticket-inside/`. `sticker-detail.png` shows the final pair. Prose draft lint: zero findings. The exact next task below stays unchanged.

## Compact stickers with larger text — October 8, 2026

The current layout follows the user's latest reference. The white sticker is wider, and the yellow sticker is smaller. Larger text fits compact boxes. The curved arrow floats above the gap. The pair stays shifted left on desktop. Ink rays attach to the yellow sticker's right corners and follow its tilt.

Nine viewport checks pass from 320 to 1920 pixels in idle and result states. They confirm text fit, no page overflow, the original grid, and no desktop scrolling. The focused Chromium shortener check, build, and lint pass. These checks use fixture data. Firefox, WebKit, and live backend checks remain open. The current captures stay in `.local/hero-ticket-inside/`. Prose draft lint: zero findings. The exact next task below stays unchanged.

Current browser commands from `frontend/`:

```bash
node .local/hero-ticket-inside/check.mjs
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'desktop shortener'
```

## Reference tickets and requested controls — October 9, 2026

The hero uses equal-height tickets with matching top and bottom edges. The white ticket is wider than the yellow ticket. Both use symmetric SVG outlines and hard shadows. Before and After labels share a baseline. The arrow and dashed cut line sit in the gap. The long URL has no strike-through. Text stays clear of the ticket notches.

The larger left section moves 16px left on desktop. The ticket group matches the headline width from the L to the question mark. Phones keep the group centered. Ink rays sit outside the yellow ticket's top-right corner. The original grid and the form/result layout stay intact.

The expiry control has one calendar trigger. Its popup contains the calendar, editable date and time, timezone hint, Clear, and Done. Calendar selection preserves the time. The field error stays beside the trigger. The calendar loads only when needed and shows a skeleton during the download.

The workspace uses a paper sidebar with grouped navigation, a yellow current-page marker, and a collapse control. Collapsed desktop navigation keeps accessible link names. Mobile collapse hides the workspace navigation until expansion. Status and analytics ranges use Base UI Select. Sort uses a searchable Base UI Combobox. Query parameters still own filter state.

Contact me opens a dialog with Name, Email, and Message fields. Open email draft prepares a mailto link to debrato2005@gmail.com. The visitor sends the message from their email app. The interface never claims delivery. Contact values stay in memory.

Feature cards, step cards, and question rows lift 6px and grow their hard shadow by 6px on hover. The shortener panel stays still. Other boxes keep the existing 2px lift. Reduced motion and touch-only pointers disable the lift. Loading states use bordered skeletons and accessible status text.

The requested Neobrutalism calendar and select compositions use Smolink token CSS. React DayPicker 9.14.0 is pinned in the package manifest and lockfile. The calendar has a separate runtime chunk. The searchable combobox uses installed Base UI instead of adding Command and cmdk. Field and sidebar examples informed the existing field and navigation structure. The skeleton follows the upstream border and pulse treatment.

The first calendar, contact, and dropdown checks failed before implementation. The hover check failed when the shortener still moved. The full Chromium fixture suite passed 29 checks before the final hover and deferred-calendar changes. Three focused checks passed afterward. They cover calendar time preservation, searchable dropdown keyboard use, stationary shortener hover, stronger card hover, reduced motion, and touch behavior.

Eight viewport checks passed from 320 to 1600 pixels. They cover headline alignment, calendar content bounds, time input, searchable choices, sidebar collapse, no horizontal overflow, axe, and browser errors. Nine additional viewport checks passed in idle and result states. They cover ticket text fit, the original grid, oval clearance, and no desktop scrolling.

Four final control checks passed in the India timezone. They cover calendar time preservation, contact drafts and mobile focus, searchable choices and sidebar collapse, and pending skeletons. Both tickets have equal height and vertical center in all 18 captured idle and result states. Five calendar license notices match the installed packages and final build byte for byte.

The final production rerun did not start. Automatic approval review failed because the workspace spend cap was reached. Four production Chromium checks passed before the final mobile contact focus change. They use injected API responses. The final source passed build, lint, and four fixture control checks. Browser screenshots remain in ignored local review folders.

The latest production receipt still needs a rerun after the workspace owner increases the approval-review spend cap. This restriction does not indicate an application failure. Firefox, WebKit, and live backend acceptance remain open.

Current commands from `frontend/`, with Node 22.23.2 and the pinned Chromium path:

```bash
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium --grep 'boxed blocks lift|calendar sets|workspace controls'
SMOLINK_E2E_REUSE=1 npm run test:e2e -- --project=chromium controls.spec.ts
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=chromium
node .local/controls-review/check.mjs
node .local/hero-ticket-inside/check.mjs
node .local/controls-review/hover.mjs
npm run build
npm run lint
npm run format:check
npm run docs:check
```

Build sizes: main JavaScript 497.97 kB (gzip 160.21 kB), calendar JavaScript 67.39 kB (gzip 19.85 kB). The calendar now loads in a separate chunk. No large-chunk warning remains. Captures stay in `.local/controls-review/` and `.local/hero-ticket-inside/`. New prose draft lint passed. All writes remain inside `frontend/`. No commit or push occurred. Root Graphify output remains outside this scope. The exact next task below stays unchanged.

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

`--sky-surface` and `--hero-surface` are frontend tokens added at the user's request. Root `docs/frontend-design-system.md` does not list them. Reconcile the root file under separate authorization. Root `graphify-out/graph.json` exists but lacks the frontend analytics modules. The graph and root documentation remain outside this task's write scope.

## Exact next task

Run the fixture and production suites in Firefox and WebKit on a host with the pinned runtimes and required host libraries. Keep the receipts separate from Chromium. Then complete FE-007 with a real backend guest-creation journey.

From `frontend/`, with the supported Node runtime and provisioned browsers:

```bash
npm run test:e2e -- --project=firefox --project=webkit
npm run build
SMOLINK_E2E_TARGET=production npm run test:e2e -- --project=firefox --project=webkit
```

Review the yellow hero highlight, ticket `cqi` sizing and notches, block hover, reduced motion, and analytics text spacing.

## Scope protections

All file writes are inside `frontend/`. No `git add`, commit, push, stash, reset, clean, or checkout command ran. No conflict resolution occurred. Root documentation, backend code, and graph output remain unchanged. Preserve `.agents/skills/` and `skills-lock.json`. `.impeccable/` remains development-only and excluded from Prettier.

## Sticker and QR loading follow-up

Moved the desktop ticket group 12px left without changing ticket sizes or alignment. Updated the arrow and scissors to match the supplied separator reference.

Replaced the dashboard skeleton in the QR dialog with one square placeholder. The dialog keeps its height when generation finishes. The download control stays disabled until the image exists.

The new Chromium checks first failed because the pending dialog contained twelve dashboard placeholders. After the fix, four focused checks passed, including real PNG download and the narrow workspace journey. Captures cover the hero and pending/ready QR states at 320px and 1440px. Build, typecheck, and lint passed. This is fixture evidence. Live QR remains unavailable. Root graph maintenance remains outside the frontend write scope.

Commands: `npm run test:e2e -- --project=chromium --grep "QR loading reserves|downloads a real QR|narrow workspace"`, `npm run build`, and `npm run lint`. Screenshots are in `test-results/fixture/controls-QR-loading-reserv-*/`. Prose lint: 0.47 findings per 100 words.

## QR skeleton appearance

Replaced the solid gray placeholder with muted SVG corner markers and soft blocks. The skeleton keeps the same dimensions as the finished QR image. The pulse uses the existing motion rule. Four focused Chromium checks passed, including pending/ready dimensions at 320px and 1440px, PNG download, and narrow workspace behavior. Build and lint passed. Captures remain in `test-results/fixture/controls-QR-loading-reserv-*/`. This is fixture evidence. Live QR remains unavailable.

Prose lint: 1.00 findings per 100 words.

## Symmetric hero reference

Matched the supplied reference with centered labels, upright scissors in the middle of the cut line, and a wider yellow ticket. Both tickets share the same height and vertical center. The highlight and supporting text now sit at the headline's center.

Three Chromium alignment checks first failed on the previous highlight and label positions. After the change, all three passed at 320px, 901px, and 1440px. The existing desktop input/output layout check also passed. Screenshot review covered phone and desktop layouts. Build, typecheck, and lint passed. The page grid, input/result behavior, and QR controls keep their existing behavior. These are fixture browser checks. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "hero tickets and separator|hero keeps|output|result below"`. Screenshots: `test-results/fixture/controls-hero-tickets-and-*/hero-symmetric.png`. Prose lint: 1.38 findings per 100 words.

## Highlight alignment correction

Restored the yellow highlight to the headline's left edge on desktop. Ticket sizes, labels, divider, scissors, and supporting text keep their existing alignment. Phones retain their centered highlight. Three focused Chromium checks passed at 320px, 901px, and 1440px.

Prose lint: 0.00 findings per 100 words.

## Ticket position correction

Moved both tickets, labels, scissors, divider, and arrow 12px left as one group on desktop. Their sizes and relative spacing stay the same. Phones keep the group centered. Three focused Chromium checks passed at 320px, 901px, and 1440px.

Prose lint: 0.00 findings per 100 words.

## Ticket cleanup and subdued footer

Moved the desktop tickets another 8px left where space permits. Narrow desktop layouts use a smaller offset after a browser check caught the first ticket outside the viewport. Reflowed the long URL, increased its font size, and cleaned the notch stroke and shadow joins.

Added a subdued footer based on the supplied reference. It contains grouped links, compact social buttons, pale contact and GitHub cards, and a creator credit. The contact card opens the existing dialog and restores focus when it closes.

Ten focused Chromium checks passed. These cover ticket alignment and text fit, footer layouts at 320px, 768px, 1051px, and 1440px, contact focus, footer axe checks, and existing navbar behavior. Build, typecheck, and lint passed. Captures are in `test-results/fixture/controls-footer-links-contact-and-*` and `controls-hero-tickets-and-*`. This is fixture evidence. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "hero tickets and separator|footer links|contact fields|navbar social|navbar items"`. Main production JavaScript: 500.90 kB, gzip 160.69 kB. Vite reported its default 500 kB chunk warning. Prose lint: 0.77 findings per 100 words.

## Footer duplication cleanup

Removed the footer social buttons, email link, account links, and extra copyright tagline. Combined navigation into one Explore section. The contact and GitHub cards remain. Four focused Chromium checks passed at 320px, 768px, 1051px, and 1440px, including contact focus, footer axe checks, link navigation, and page overflow. Build, typecheck, and lint passed. Screenshot review covered the updated desktop footer. These are fixture checks. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "footer links"`. Prose lint: 1.60 findings per 100 words. Main production JavaScript: 500.48 kB, gzip 160.64 kB. The default Vite chunk warning remains.

## Stronger footer and creator destination

Strengthened the footer borders and shadows, squared its card corners, and added yellow brand and creator accents. Changed the creator link from X to GitHub. Four focused Chromium checks passed at 320px, 768px, 1051px, and 1440px, including creator destination, contact focus, link navigation, footer axe, and page overflow. Build, typecheck, and lint passed. These are fixture checks.

The requested Buy me a coffee button needs the user's support URL. A question is pending. No payment destination was guessed. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "footer links"`. Prose lint: 2.27 findings per 100 words.

## Footer reference layout

Rebuilt the footer around the new image reference. Enlarged the original logo, added the Long story, smol link headline, and grouped real links under Product and Resources. The repository action appears once beside the styled coffee button. The creator card opens the GitHub profile. Contact remains available through Say hello. The coffee button stays disabled pending the user's support URL.

Five focused Chromium checks passed, covering four footer widths, creator and repository destinations, contact focus, footer axe, overflow, and existing navbar social behavior. Build, typecheck, and lint passed. Captures remain in `test-results/fixture/controls-footer-links-contact-and-*/footer.png`. These are fixture checks. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "footer links|navbar social"`. Prose lint: 1.08 findings per 100 words. Main production JavaScript: 500.81 kB, gzip 160.79 kB. The default Vite chunk warning remains.

## Footer support links

Added OnlyChai with the user's exact support URL. Renamed Buy me a coffee to Ko-fi. Ko-fi remains disabled while the profile URL is pending.

The existing footer check first failed because OnlyChai was absent. After the change, four focused Chromium checks passed at 320px, 768px, 1051px, and 1440px. These cover the support destination, disabled Ko-fi state, contact focus, navigation, accessibility, and page overflow. Reviewed desktop and phone screenshots. Build, typecheck, and lint passed. These are fixture checks. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "footer links"`. Main production JavaScript: 501.02 kB, gzip 160.85 kB. The default Vite chunk warning remains. Next task: connect Ko-fi after the user supplies its profile URL.

Prose lint: 1.35 findings per 100 words.

## Compact footer

Reduced the footer to small branding, creator credit, copyright, contact, and support actions. Removed repeated copy, navigation columns, the repository button, and the large creator card. The desktop row wraps when needed. Phones use equal support columns.

The compact-height check first failed at 1440px: the footer was about 599px tall. After the change, four Chromium checks passed at 320px, 768px, 1051px, and 1440px. These cover height limits, page overflow, home navigation, contact focus, support state, and accessibility. Reviewed phone, tablet, and desktop screenshots. Build, typecheck, and lint passed. These are fixture checks. Root graph maintenance remains outside the frontend write scope.

Command: `npm run test:e2e -- --project=chromium --grep "footer links"`. Captures: `test-results/fixture/controls-footer-links-contact-and-*/footer.png`. Next task: connect Ko-fi after the user supplies its profile URL.

Prose lint: 0.99 findings per 100 words.
