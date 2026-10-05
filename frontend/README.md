# Smolink frontend engineering

This document owns frontend engineering rules. It extends the project's
backend-first plan without selecting or installing a frontend stack.
Implementation requires a separately authorized milestone.

## Owners and authority

| Owner | Responsibility |
| --- | --- |
| [Project README](../README.md) | Architecture decisions, invariants, API targets, and endpoint status |
| [Frontend plan](../docs/ENGINEERING_PLAYBOOK.md#frontend-design) | Product intent and suggested frontend structure |
| This document | Frontend boundaries, design, motion, accessibility, and acceptance rules |
| [Build checklist](../docs/backend-build-checklist.md#planned-full-product-follow-on) | Product queue, tool candidates, and dated milestone receipts |
| [Walkthrough](../docs/codebase-walkthrough.md#tests-and-verification-limits) | Current implementation and test limits |
| [Authentication design](../docs/superpowers/specs/2026-08-01-authentication-authorization-design.md) | Authentication target and unresolved delivery contracts |
| [Agent Guide](../docs/AGENT_GUIDE.md) and [agent tooling](../docs/agent-tooling.md) | Authorization, skills, terminology, and generated-output policy |

Read the root [AGENTS.md](../AGENTS.md) before work. The project README owns
the [testing policy](../README.md#testing-policy). This document does not
replace those owners or create another implementation queue.

## Destination assessment: October 5, 2026

This assessment describes the inspected worktree, not a running application.
`frontend/` was empty before this document. No frontend-specific instructions,
source, package manifest, lockfile, scripts, generated types, or tests existed.
There was no router, styling system, token set, font, theme, motion owner,
media, SEO configuration, browser-support matrix, or measured performance.
No `.github/` directory or repository documentation verifier was found.

The backend uses FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Redis, and `uv`.
Its [manifest](../backend/pyproject.toml) and lockfile govern backend dependencies.
Compose starts PostgreSQL and Redis only. React with TypeScript is the existing
frontend plan, not an installed implementation. The plan names component and
visual candidates. Their presence in prose does not approve installation.

Root and `docs/` files already contained uncommitted testing-policy edits.
This task preserves them. Endpoint and frontend-plan status agree with the
inspected source and committed documentation. The worktree adds explicit
behavior-first testing guidance. Historical test receipts are not fresh passes.

| Area | Classification | Evidence and documentation decision |
| --- | --- | --- |
| HTTP ownership and guest creation | KEEP | The README and [URL route](../backend/app/api/v1/endpoints/urls.py) preserve guest ownership and HTTP access. Keep database access in the backend. |
| Test selection and manual learning | KEEP | The README and Agent Guide favor realistic boundaries and user-directed steps. Preserve both policies. |
| Frontend architecture and visual rules | REFINE | The Playbook gives suggested directories, but no frontend exists. Specify responsibilities and acceptance without generating a folder tree. |
| Error handling contract | REFINE | Domain errors use `error` and `message`. Validation and authentication dependencies use `detail`. Require one frontend parser until backend normalization is authorized. |
| Authentication and deployment | DEFER | Token storage, refresh coordination, browser binding, and API origin policy need decisions before integration. The authentication design records pending Google delivery. |
| Dashboards, redirects, QR, analytics | DEFER | The README marks their endpoints planned. Do not expose working controls or fabricate records. |
| Scroll stories and GPU effects | DEFER | The checklist lists candidates, but no measured product need or renderer exists. Keep adoption conditional. |

No application refactor, replacement, or removal follows from these classifications.

## Small architecture and deliberate dependencies

Keep feature state near its consumer. Let the selected router own URL context.
Keep server state in one owner, with explicit refresh and invalidation rules.
Do not create a second store for the same response.

Keep API transport, response parsing, authentication, mapping, and errors behind
small interfaces. Add shared components or abstractions for concrete consumers.
The Playbook's directory suggestions do not require empty folders, registries,
generic utility frameworks, or a wrapper for every function.

Prefer semantic HTML, native controls, and existing code. A complex control
needs a consumed interaction and keyboard/focus acceptance. Use one router,
styling system, component system, and motion owner for each responsibility.
Do not import OncoSyn's components, assets, composition, or timing constants.

Before a dependency decision, inspect native APIs and installed alternatives.
Record the consumer, alternatives, compatibility, maintenance, license,
transitive cost, bundle cost, provenance, and required acceptance in this document.
Link the originating reference and distinguish copied recipes from original work.
The future lockfile owns exact versions. Adopt only consumed recipe pieces.
Framework, package manager, build, and deployment changes need their own scope.

## API, state, and truthful feedback

Use the implemented HTTP contracts. Never connect a browser to PostgreSQL or
Redis. Keep wire types separate from display models. If type generation is
selected, generate from the backend contract and never edit outputs by hand.
Types do not replace runtime checks of shape, identity, and response context.

The [URL schema](../backend/app/schemas/url.py) returns `id`, `short_code`,
`short_url`, destination, expiry, and creation time. Preserve these meanings.
Use the returned public URL rather than inventing a deployment host.
Creation success does not prove redirect availability: that route remains planned.
Custom aliases use creation and its conflict response. There is no live alias check.

Idle, loading, ready, confirmed empty, partial, stale, error, blocked, and
unavailable are candidate states. Use only states supported by each contract.
A failed request is not an empty result. A missing analytics route is not
zero clicks. Label fixtures at their source and retain the label through
navigation, screenshots, and exports. Do not invent persistence or metrics.

Cancel obsolete reads. Reject late responses when cancellation cannot prevent
stale writes. Check returned identity against the active resource or account.
Prevent duplicate submissions while a mutation is pending. Do not automatically
retry a mutation without a documented safe-retry contract.
If a timeout leaves the outcome unknown, describe that uncertainty.

| Outcome | Frontend rule |
| --- | --- |
| `201` creation | Show the returned result after response checks. Do not claim a tested redirect. |
| `409` alias conflict | Preserve input and show an actionable alias error. |
| `422` | Parse the actual envelope and associate safe field errors with inputs. |
| `401`, `403`, `423` | Distinguish invalid authentication, denied access, and account lock. Never silently retry authenticated creation as a guest. |
| `429` | Use a valid `Retry-After` value in seconds. Bound recovery and do not retry in a loop. |
| `503`, network failure, invalid response | Show unavailable or error state. Do not report success or empty data. |
| Empty `202` | Confirm request acceptance only. Forgot-password and resend do not confirm account existence or email delivery. |
| `204` | Handle the empty body without attempting JSON parsing. |

Parse domain `error`/`message` and FastAPI `detail` in the transport owner.
Expose safe feedback, not raw payloads, private identifiers, or stack traces.
Keep expected failures distinct from correctness defects. Clipboard success
requires a successful clipboard operation. Show manual-copy recovery on failure.
Only decorative failure can quietly retain a static fallback.

## Authentication, privacy, and unresolved boundaries

Route guards improve navigation. The backend owns authorization. Guests must
retain creation access. A supplied invalid Bearer token must not silently lose
ownership through a guest fallback. Preserve the backend's account-state-neutral
recovery responses in interface wording.

The [auth schemas](../backend/app/schemas/auth.py) return token pairs as JSON.
The current routes do not establish a cookie session. Decide token storage,
reload behavior, refresh coordination, logout, and expired-session recovery
before implementation. Concurrent refreshes must respect single-use rotation.
Do not default to persistent browser token storage or invent cookie support.
Keep passwords, tokens, and secrets out of logs, analytics, screenshots, and exports.
Client-visible build variables cannot hold secrets.

Email links currently target `/verify-email#token=...` and
`/reset-password#token=...`, as the [sender](../backend/app/services/email_service.py)
defines. Their frontend pages remain planned. Consume fragments only inside
the responsible flow and clear them from the displayed URL when possible.
Do not convert these tokens to query parameters or send them to telemetry.
Google sign-in requires the unresolved browser-binding and delivery contract.

Resolve these boundaries in their existing owners before dependent UI work:

- **Numeric IDs:** schemas return integer Snowflake IDs. Establish lossless browser handling before numeric owner routes. Do not stringify an already rounded JavaScript value.
- **API origin:** [application startup](../backend/app/main.py) configures no CORS middleware or frontend serving. Choose same-origin routing or an explicit cross-origin policy before browser integration.
- **Deployment routes:** define API, public short-link, frontend route, and reload behavior without shadowing `/api/v1`, `/health`, or future short codes.
- **Privacy:** define allowed persistence and retention for user data. Do not infer permission from browser-storage availability.

These are contract decisions, not authorization to change backend source.

## Visual grammar and accessible interaction

Start with the creation form and its result. Keep URL entry, alias, expiry,
errors, and copy actions clear. Authentication and future management surfaces
need stable, task-focused controls. A separate public visual system needs an
actual storytelling requirement.

Define semantic tokens for type, hierarchy, spacing, color, density, borders,
radii, icons, focus, and interaction states when implementation starts.
There are no existing frontend tokens to extend yet. Select fonts with license,
loading, fallback, and layout behavior in mind. Study reference principles
without copying their branding, text, assets, DOM, or composition.

The frontend acceptance target is
[Web Content Accessibility Guidelines (WCAG) 2.2, Level AA](https://www.w3.org/TR/WCAG22/).
This is a target, not a conformance claim. Use semantic landmarks, logical
headings, accessible names, DOM order, and visible focus. Check route titles
and focus. Dialogs and menus need keyboard dismissal and focus restoration.
Label forms and describe expiry units and timezone. Associate errors with fields.
Announce important status changes without moving focus unexpectedly.

Check keyboard use, touch, zoom, reflow, text spacing, contrast, and reduced
motion in rendered pages. Color alone cannot convey status. Test long URLs,
unbroken aliases, error text, and sticky controls. Preserve table relationships
and comparisons if owner listing or analytics tables arrive.
Choose breakpoints from content. QA widths of 390, 768, 1024, and 1440 pixels
are samples, not breakpoints or a complete browser-support matrix.

Define supported browsers and input methods before release. Automated
accessibility scans and token contrast checks support review, but cannot
establish full conformance or rendered contrast by themselves.

## Motion, media, and performance

Each animation needs a purpose: comprehension, continuity, state change, or
restrained delight. Start with CSS and native browser APIs. Keep forms, tables,
errors, and status labels stable. Prefer transform and opacity where suitable.
Do not update framework state each frame without a concrete requirement.
The initial reduced-motion mode must show settled, readable content.

An installed motion tool earns use through a consumed transition. Timelines
need coordinated choreography. GPU rendering needs a demonstrated rendering
requirement. Keep observers, timers, subscriptions, and renderer resources in
their owner. Release them on unmount and mode changes.

If a scroll narrative is later justified, use one normalized progress value.
Derive scenes and media from that value. Do not combine competing scroll
controllers and autoplay clocks for the same geometry. Keep sticky wrappers
stable and animate descendants. Measure after fonts and layout settle.
Recompute on relevant resize. Check reverse scroll, restored intermediate
positions, arbitrary jumps, entry, and release. Supply readable normal flow
for reduced motion and unsuitable viewport geometry. If GSAP and Lenis are
adopted, define one timing owner and explicit cleanup rather than importing
another project's ticker settings.

Keep ordinary prose stable. A rare text effect must reserve final geometry,
retain accessible text, and survive font delays, interruption, and route revisits.
Interactive meaning cannot depend on hover alone.

Use SVG for suitable diagrams. Canvas, WebGL, video, and frame sequences need
a consumer and a cost review. Essential content stays in semantic DOM.
Reserve media geometry, use responsive assets, and lazy-load heavy owners.
Pause hidden or offscreen work. Define slow-network, failed-asset,
unsupported-renderer, reduced-motion, and low-resource fallbacks where relevant.
Bound frame fetch/decode concurrency and decoded memory. Release decoded
resources. Persistent GPU backgrounds need continuity without repeated context
creation. Measure before selecting pixel-ratio caps or performance budgets.

Measure relevant build chunks, loading, rendering, layout shifts, and input
responsiveness after an app exists. Record build, route, browser, device/profile,
data scale, tool, result, and limits. Source inspection cannot promise frame rate.
Asset placement and page metadata follow the selected build system. Decide
indexing rules for public and account pages before release. Never expose private
data or tokens in titles, previews, or metadata.

## Verification and tools

Use the README testing policy and
[Playbook selection questions](../docs/ENGINEERING_PLAYBOOK.md#test-quality-and-coding-agents).
For behavior changes, establish a reproducible failing check at the highest
practical boundary. Then implement the minimum correction and rerun relevant
checks. Units need distinct fault-detection value. Tests must not freeze vendor
names, decorative constants, private structure, or framework internals.

Browser E2E remains planned. Once the necessary backend routes exist, test
critical guest creation/redirect, local authentication, recovery, logout, and
owner workflows against the real stack. Use controlled external-provider doubles.
An intercepted browser response proves frontend behavior, not database persistence,
email delivery, or a complete workflow. Existing backend tests provide historical
evidence only unless rerun in the stated environment.

For meaningful visual changes, inspect rendered pages before acceptance.
Capture a useful before-state for major redesigns. Check representative widths,
keyboard, route changes, reload, resize, reduced motion, slow loading, and failure
states. Exercise reverse scroll and intermediate states when motion uses scroll.
Record physical touch or other inputs that remain untested. Inspect viewport
captures as well as full-page captures. Stitched images can misrepresent fixed
backgrounds. Source decides semantics. Rendered behavior decides visual acceptance.

The documentation-task inspection on October 5 found these capabilities:

- Repository skills: `fastapi`, `python-testing`, and `graphify`. Read applicable instructions before use. No frontend-local skills existed.
- Installed `asd-ste100`: technical prose guidance and a locally executable linter. Its score does not certify meaning or conformance.
- Graphify: a callable CLI and existing graph. A query worked but warned about legacy node IDs. Use it for navigation and check source. Do not rebuild generated data during documentation-only work.
- Figma and Firecrawl: connector tools exposed in this chat. Account access and successful execution were not tested. Availability must be rediscovered in another session.
- Frontend build, lint, formatter, browser runner, axe, performance tools, and CI: no repository setup found. Playwright, axe, Lighthouse, profilers, Storybook, and visual regression services are optional candidates, not installed capabilities.

Do not install a tool to satisfy a documentation task. Figma and diagrams can
help substantial design work. They are unnecessary for a small patch.
Do not copy origin skill bundles or treat a named tool as required infrastructure.

## Installed frontend skills

Installed October 5, 2026, in `.agents/skills/`. The
[skill manifest](skills-lock.json) records upstream repositories, pinned commits,
installed paths, declared names, file counts, and content hashes.
These are agent guidance bundles, not application dependencies.
Read the relevant skill before use. Project instructions and the README
testing policy override conflicting bundle guidance.

| Skill | Use |
| --- | --- |
| [impeccable](.agents/skills/impeccable/SKILL.md) | Product UI, design, audit, accessibility, polish, and motion |
| [ui-ux-pro-max](.agents/skills/ui-ux-pro-max/SKILL.md) | Local research for typography, colors, layout, UX, and stack guidance |
| [design-taste-frontend](.agents/skills/design-taste-frontend/SKILL.md) | Public landing pages and redesigns, within its stated scope |
| [react-best-practices](.agents/skills/react-best-practices/SKILL.md) | React performance when React implementation starts |
| [web-design-guidelines](.agents/skills/web-design-guidelines/SKILL.md) | Interface and accessibility review |
| [ponytail](.agents/skills/ponytail/SKILL.md) | Native capabilities, reuse, and scope restraint |
| [investigate-first](.agents/skills/investigate-first/SKILL.md) | Evidence-based diagnosis before a fix |
| [surgical-patch](.agents/skills/surgical-patch/SKILL.md) | Narrow fixes at the responsible boundary |
| [safe-refactor](.agents/skills/safe-refactor/SKILL.md) | Structural changes that preserve behavior |
| [lean-build](.agents/skills/lean-build/SKILL.md) | Bounded features with an explicit stop condition |
| [verify-and-stop](.agents/skills/verify-and-stop/SKILL.md) | Proportionate acceptance checks without scope expansion |
| [caveman](.agents/skills/caveman/SKILL.md) | Concise communication when requested, subject to the project writing policy |
| [playwright](.agents/skills/playwright/SKILL.md) | Browser interaction and captures through a CLI |
| [playwright-interactive](.agents/skills/playwright-interactive/SKILL.md) | Persistent browser interaction when the required runtime is available |
| [screenshot](.agents/skills/screenshot/SKILL.md) | Operating-system screenshots when requested and supported |

The React bundle declares `vercel-react-best-practices`. Its Next.js guidance
applies only if Next.js is separately selected. These skills do not select
frameworks, component libraries, animation packages, or deployment platforms.
Figma, Firecrawl, and writing skills remain available through the session's
existing installations. Backend skills remain in the repository's root
`.agents/skills/`. Do not duplicate them here.

Installation checks covered upstream content, declared names, launcher syntax,
and local UI/UX search. Browser capture and the Impeccable engine were not run.
The Impeccable launcher can download its pinned engine on first use. The
Playwright CLI needs `npx` and its browser runtime. OS screenshots need a
supported capture tool and display access. `playwright-interactive` requires
`js_repl`, which this installation session did not expose. Its upstream workflow
also specifies a different sandbox mode. Installation does not change runtime
features or sandbox policy. Check these prerequisites before invoking a skill.

## Bounded changes and completion evidence

Inspect Git status and targeted dirty diffs before edits. Preserve user work.
Use narrow patches. Respect the Agent Guide's manual learning workflow unless
the user authorizes implementation. A useful vertical slice includes UI,
interaction, transport, supported states, accessibility, relevant checks, and docs.
Do not generate an application for a narrow request.

Use skills that materially help the task. Avoid automatic skill chains and
reviewer rituals. Delegate only independent work with clear ownership and
material benefit. Repeat a passed check only after relevant changes or stale
evidence. Report new failures separately from pre-existing failures.

Record each receipt in the existing build checklist with the exact command or
manual action, observed result, date, environment, scope, and evidence limits.
Use `PASS`, `FAIL`, `BLOCKED`, and `NOT RUN` accurately. Do not rewrite historical
results as current acceptance. Frontend implementation also requires updates
to the existing walkthrough, according to the Agent Guide.

Documentation-only changes need source agreement, local link/anchor checks,
prose review, whitespace checks, and a final write-boundary comparison.
Use existing document and formatting scripts if present. This checkout had
none for the frontend. Do not run an application suite automatically or repair
source to make documentation true. Preserve source, tests, configuration,
lockfiles, generated outputs, media, skills, and unrelated documentation edits.
Run `git diff --check` from the repository root. Review new untracked documents
separately because the ordinary Git diff does not include them.
