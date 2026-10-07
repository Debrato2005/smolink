# Testing and quality

**Owner:** Frontend test strategy and acceptance gates

## Test selection

Use the root [testing policy](../../README.md#testing-policy) and [Playbook questions](../../docs/ENGINEERING_PLAYBOOK.md#test-quality-and-coding-agents). Test important behavior at the highest realistic boundary that gives deterministic, useful feedback.

Before adding a test, name the break it detects. Check whether a higher boundary already detects that break. Selective tests need distinct diagnostic or fault-detection value. Counts and coverage are not quality targets. Do not test static component constants, imports, getters, or private structure.

For behavior changes, observe a reproducible red check, implement the smallest correct change, then observe green. Configuration and documentation use meaningful executable/structure checks instead of fabricated units.

## Current layers and evidence limits

Vitest uses the Node environment. Focused checks cover explicit source selection, unsafe origins, lossless-ID refusal, malformed responses, mixed HTTP envelopes, empty bodies, timeout/cancellation, and explicit token attachment. HTTP tests use a real ephemeral loopback server and native Fetch. They do not require PostgreSQL, Redis, or a guessed live backend.

Playwright runs the actual React/Vite app. The browser suite uses the one explicit fixture adapter. It covers preview/result, unavailable routing/reload, fallback recovery, console errors, absence of fixture API calls, keyboard skip focus, reduced motion, reflow, and axe scans.

The production suite serves built assets and injects an HTTP 503 response at the network boundary. It checks live transport, visible failure, no fixture fallback, empty browser storage, and email-fragment removal. Failure injection is not backend integration evidence.

Fixture browser tests prove frontend behavior only. They do not prove database persistence, rate-limit enforcement, backend authorization, redirect correctness, email delivery, OAuth, or a real-stack journey. Future live checks must use the real Smolink stack and controlled external-provider doubles.

Testing Library is evaluated but not installed. Current interaction confidence comes from the real browser. Add component tests only when a concrete behavior needs faster distinct feedback. Use user-facing queries and interactions if adopted. Do not install a DOM emulator solely to test static markup.

## Browser matrix

| Boundary                  | Target                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------ |
| Automated desktop engines | Pinned Playwright Chromium, Firefox, WebKit                                          |
| Responsive samples        | 390, 768, 1024, and 1440 CSS px                                                      |
| Reflow                    | 320 CSS px with no page overflow or lost task                                        |
| Motion                    | Normal and `prefers-reduced-motion: reduce`                                          |
| Manual accessibility      | Keyboard order, visible focus, zoom/text spacing, screen-reader landmarks and status |
| Release device checks     | Physical touch and Safari/iOS/Android on supported devices before release            |

WebKit is an engine check, not physical Safari certification. A configured project is not a passing run. Record installed engines, command scope, failures, host-library blockers, and unrun device checks in the handoff.

## Browser and accessibility review

Inspect actual viewport captures together at desktop and mobile widths. Use a bounded correction pass for material findings. Passing source, typecheck, or axe does not establish visual acceptance. Full-page stitched images can hide fixed/sticky behavior. Inspect viewport captures for those systems.

Check console/page errors and relevant requests. Inspect field labels, focus appearance, active navigation, disabled/loading states, failure feedback, long values, reload, resize, and native history. For future scroll effects, add forward/reverse travel, intermediate entry, restored scroll, and resize checks.

Axe scans use applicable WCAG 2/2.1/2.2 AA tags. Scans supplement contrast and manual checks. They do not prove focus order, every state, screen-reader comprehension, cognitive usability, or whole-product conformance.

## Production and performance gate

Run a live production build and inspect its asset output. Production must reject fixtures and contain no fixture chunk or `.invalid` sample URL. Inspect the production app in a real browser, including an API failure path. A fixture dev screenshot cannot prove production behavior.

Review compressed JavaScript/CSS, bounded font faces, and duplicate/heavy packages. Record build, environment, browser, data scale, and measurement limits. Do not promise frame rate or Core Web Vitals from code. No artificial performance budget applies before product flows exist.

Future feature reviews must check cleanup of listeners/timers/observers, stale responses, cancelled requests, duplicate submission, safe mutation recovery, and account/resource changes. Heavy visuals need a lazy boundary, static fallback, and measured interaction cost.

## Privacy and milestone completion

No frontend secret, token persistence, URL telemetry, raw error display, or third-party font request is acceptable in this foundation. Verify fragment removal before captures on email routes. Later auth needs a separately settled delivery, storage, browser-binding, and refresh contract.

Run from `frontend/`:

```bash
npm run docs:check
npm run typecheck
npm run lint
npm run format:check
npm test
npm run test:e2e
npm run build
SMOLINK_E2E_TARGET=production npm run test:e2e
```

Also inspect rendered captures, production behavior, final Git status, all new files, and `git diff --check`. Compare outside-frontend state against the initial baseline. Existing dirty root paths are preserved work, not task modifications.

A milestone becomes `DONE_VERIFIED` only when its stated acceptance runs succeed. A blocked browser engine remains blocked. A mock does not satisfy a live gate. Stable test rules stay here. Exact dated command receipts belong in [HANDOFF.md](HANDOFF.md).
