# Frontend performance audit

**Owner:** Dated performance audit and optimization evidence

Date: October 12, 2026 (Asia/Calcutta).

The frontend transfers fewer bytes and does less startup work. The interface remains unchanged in completed visual and interaction checks. Changes stay inside `frontend/`. No dependency, API, authentication contract, infrastructure, commit, push, or deployment changed.

## Baseline versus optimized

Mobile values are medians of three runs. kB means 1,000 bytes.

| Metric                                         | Before      | After       | Change                                |
| ---------------------------------------------- | ----------- | ----------- | ------------------------------------- |
| Lighthouse mobile performance                  | N/A         | N/A         | Lighthouse is not installed or cached |
| LCP                                            | 1.572 s     | 1.348 s     | 14.2% lower                           |
| INP / lab responsiveness proxy                 | 152 ms      | 192 ms      | Proxy increased. Field INP is N/A     |
| Isolated response proxy, five alternating runs | 128 ms      | 112 ms      | 12.5% lower, with overlapping ranges  |
| CLS                                            | 0.01751     | 0.01751     | Unchanged                             |
| FCP                                            | 476 ms      | 504 ms      | 28 ms higher                          |
| TBT / startup blocking proxy                   | 137 ms      | 61 ms       | 55.5% lower                           |
| Initial JS transferred                         | 163.10 kB   | 133.48 kB   | 18.2% lower                           |
| Total JS bundle size, uncompressed             | 576.52 kB   | 483.17 kB   | 16.2% lower                           |
| Main-thread task duration, fixed workload      | 1,760 ms    | 1,481 ms    | 15.9% lower                           |
| Initial resource count                         | 11          | 11          | Unchanged                             |
| Initial resource bodies                        | 2,304.63 kB | 1,503.48 kB | 34.8% lower                           |
| Three brand image bodies                       | 2,047.52 kB | 1,275.99 kB | 37.7% lower                           |
| Slowest image request duration                 | 10.85 s     | 6.99 s      | 35.6% lower                           |
| TTFB, local preview                            | 3.2 ms      | 3.4 ms      | Does not measure a deployed server    |

Desktop medians: LCP 224 → 152 ms, FCP 56 → 48 ms, CLS 0.00270 → 0.00270. The interaction proxy remains 40 ms. The startup blocking proxy remains 0 ms.

### Method and limits

The environment uses WSL Linux, Node 22.23.2, Vite 8.3.2, and pinned Playwright Chromium 153.0.8010.12. Both samples serve production builds with Vite preview. The original build remains archived locally. Each sample uses a fresh browser context with the HTTP cache disabled. Fonts and images finish before the interaction sequence.

Mobile emulation uses 390 × 844 CSS pixels, DPR 2, touch input, 4× CPU slowdown, 1.6 Mbps download, 750 kbps upload, and 150 ms configured network latency. Desktop uses 1440 × 900 without throttling. This is an Android-class laboratory proxy, not physical device or field evidence.

PerformanceObserver records LCP, FCP, layout shifts, long tasks, and Event Timing. The CLS value sums shifts without recent input in this short session. The blocking proxy sums each startup long task's duration above 50 ms. It is not Lighthouse TBT. The interaction proxy is each run's slowest recorded interaction while entering a URL and opening expiry controls. It is not field INP. The task duration includes startup, typing, and the first calendar opening.

Resource counts use completed Resource Timing entries. They exclude HTML and browser-managed favicon requests. Transfer sizes include the recorded header allowance. Cross-origin badge timing is excluded. The public GitHub badge uses a fixed SVG response in the harness. Its real service latency remains unknown.

The three-run timing sample is small. Mobile LCP ranges are 1.512–1.748 s before and 1.332–1.400 s after. FCP and interaction timing did not improve consistently. No responsiveness improvement or field Core Web Vitals pass is claimed.

The higher initial response proxy prompted five alternating before/after interaction runs. These use the same 4× CPU slowdown after resources settle, without network throttling or competing test suites. Medians are 128 → 112 ms, with ranges of 88–152 ms and 96–160 ms. The overlapping results do not establish a response regression or a consistent improvement. `interaction.json` retains all samples.

The [audit harness](../scripts/performance-audit.js) saves metrics, CDP traces, and screenshots under ignored `.local/performance/`. Run from `frontend/` with the production preview available:

```bash
node scripts/performance-audit.js before
# Apply a change and rebuild before the next capture.
node scripts/performance-audit.js after
```

Set `PLAYWRIGHT_BROWSERS_PATH` to the installed runtimes when needed. `AUDIT_URL` selects the preview. `SAMPLE_RUNS` selects the sample count. `SKIP_SHOTS=1` skips screenshots. `SKIP_METRICS=1` skips profiling. Local receipts include `before/metrics.json`, `after/metrics.json`, desktop/mobile traces, screenshot comparisons, and `lifecycle.json`.

## Changes implemented

### 1. Remove unreachable fixture workspace code from production

The live workspace layout already returns its existing availability notice before rendering its child routes. Dashboard, details, and analytics imports still added their modules and Base UI selection code to the production bundle.

`src/app/App.tsx` now gates those three route elements with the existing Vite `DEV` constant. Production removes their unreachable module code. Development retains eager workspace components. All route paths and the production notice remain. Essential creation, authentication shells, contact, and expiry controls remain eager or retain their existing calendar boundary. No new loading state or Suspense boundary exists.

The main chunk changes from 500.22 kB / 160.65 kB gzip to 406.88 kB / 130.80 kB gzip in Vite's build report. The existing calendar chunk remains unchanged. The build's large-chunk warning disappears. An artifact check first failed at equal total JS sizes, then passed after optimization.

Trade-off: future live workspace integration must remove these gates when its gateway and session contracts become available. `tests/e2e/production.spec.ts` now checks every existing workspace path and its return to guest creation, with zero owner requests.

### 2. Serve lossless brand WebP files

The three PNGs supplied 2.05 MB on each uncached homepage load. Their rendered dimensions are much smaller than their source dimensions.

Added `public/smolink-logo.webp`, `public/smolink-symbol.webp`, and `public/smolink-wordmark.webp`. Updated image paths in `App.tsx` and `WorkspaceLayout.tsx`. ImageMagick used `-define webp:lossless=true -define webp:exact=true`. All dimensions and decoded pixels match the originals. Each image comparison reports zero changed pixels. CSS, SVGs, icons, source PNGs, and the favicon remain unchanged.

Trade-off: source PNGs remain in public output for provenance and existing asset URLs. The distribution contains both formats. Browsers request only the WebP versions for these brand elements. This reduces transfer, not the total distribution's disk footprint.

### 3. Repair regression checks

The reload test referenced a removed footer link. It now uses the existing desktop or mobile navigation and waits for smooth scrolling. Firefox reported 499.9999847 px for a 500 px panel and fractional float differences during hover. Geometry checks now allow subpixel rounding while retaining their size and motion assertions. These changes affect tests only.

## Regression verification

| Area                                 | Result and boundary                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Visual parity                        | Passed controlled Chromium comparisons at 390, 768, and 1440 px. No observed design change             |
| Component behavior and navigation    | Passed fixture and production checks in Chromium and Firefox                                           |
| Forms and URL creation               | Passed fixture journeys and production HTTP response injection. Live backend N/A                       |
| Authentication                       | Fixture journeys and production disabled/unavailable behavior passed. Live authentication N/A          |
| Dashboard and analytics              | Fixture journeys passed. Production availability notice passed on all existing paths                   |
| Responsive layouts                   | Passed browser samples including 320 px reflow and 1920/2560 px workspace checks                       |
| Animation, scrolling, reduced motion | Passed hover, reload, keyboard, and touch checks. CSS timing remains unchanged                         |
| Accessibility                        | Keyboard, focus, reflow, text-spacing, and axe checks passed. Manual screen reader checks N/A          |
| Type checking, lint, formatting      | Passed                                                                                                 |
| Tests                                | 9 contract/HTTP tests passed. 10 production cases passed across Chromium and Firefox                   |
| Fixture suite                        | Final combined run: 84/86 passed. The two timing failures passed in a serial rerun covering four cases |
| Production build                     | Passed. No fixture URLs, fixture gateway, or test-token strings in shipped JS                          |
| Browser console                      | No page or console errors in the six production measurement runs                                       |
| WebKit                               | BLOCKED: missing `libevent-2.1-7t64` and `libgstreamer-plugins-bad1.0-0`. No host package changes      |

Initial screenshot differences included a sticky header at different scroll positions and hover state. Controlled repeats resolved them. Forty-six production captures match exactly. The email-page repeat has identical bounds and zero changed pixels. The first fixture comparison matched 13 of 15 captures. Controlled original-PNG versus WebP comparisons matched all 15 fixture captures. Original captures and diagnostic comparisons remain available locally.

Twenty route/calendar/contact cycles retain 403 DOM nodes, four documents, and 334 listeners in both builds after garbage collection. Heap rises from 4.75 to 6.65 MB before and 4.69 to 6.57 MB after. This does not prove that heap retention is bounded. No new listener or DOM accumulation appeared in this sequence.

## Remaining bottlenecks

| Finding                                 | Evidence and severity                                                                    | Next investigation                                                                      |
| --------------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Brand resolution exceeds displayed size | Verified. Medium. Lossless conversion still transfers 1.28 MB                            | Evaluate responsive image candidates at multiple DPR values with visual acceptance      |
| First calendar interaction              | Verified laboratory variability. Medium. Calendar remains 67.39 kB plus 7.96 kB CSS      | Repeat isolated interaction traces before changing resource scheduling                  |
| Font-related shifts                     | Small measured CLS remains. Low. Existing self-hosted faces and swap behavior remain     | Attribute shift sources before choosing preload or metric-compatible fallback changes   |
| Heap growth across repeated cycles      | Verified growth in both builds. Cause unknown. Low in this bounded sequence              | Inspect retained objects and longer sequences before changing lifecycle logic           |
| Delivery policy                         | Deployment compression, immutable asset cache, HTML cache, CDN, and API TTFB are unknown | Settle the external hosting contract and measure its headers and latency                |
| Live product integration                | Existing backend/session boundaries remain blocked                                       | Complete the canonical contracts before real authentication and owner performance tests |

No broad memoization, dependency removal, cache layer, virtualization, animation replacement, or architecture rewrite was justified. Existing resource reads cancel on unmount. Dashboard filters use local data and render six rows per page. Analytics reads run in parallel. No graphics render loop exists.

Root README statements that frontend/browser journeys remain planned conflict with current frontend source and tests. Root Graphify output also lacks current frontend relationships. Root documentation and graph maintenance remain outside the frontend write boundary.

## Result

Production ships less JavaScript and transfers smaller brand assets. Mobile LCP, startup blocking work, and total recorded task duration improve in this laboratory sample. Interaction and FCP results remain uncertain. No observed visual or functional difference remains in completed checks. WebKit, physical devices, field INP, and real-stack acceptance remain unverified.

Prose lint: 0.89 mechanical findings per 100 words. This score does not certify full ASD-STE100 compliance.
