# Frontend architecture

**Owner:** Stable frontend architecture

## Runtime and module direction

React and TypeScript run as a Vite single-page application (SPA). React Router declarative mode owns browser paths. npm owns one exact lockfile. The [Source Ledger](SOURCE_LEDGER.md) owns versions and alternatives.

Use this direction:

```text
app composition → routes → feature interaction → gateway interface
                                             → shared UI primitives
live gateway → HTTP transport → unknown wire data → validated adapter → frontend model
fixture gateway → the same adapter and frontend model
```

`src/app/` composes the router and dependencies. `src/routes/` composes pages. `src/features/shorten/` owns destination form state and requests. `src/components/ui/` owns consumed shared controls. `src/lib/api/` owns transport and contract interpretation. `src/lib/config/` owns source selection and API configuration. `src/styles/` owns tokens and shared styling.

Low-level API/configuration modules must not import routes or features. Features must not import another feature's route implementation. Keep direct imports. Add a folder only when it has a consumer. Do not build empty auth, dashboard, analytics, provider, or utility layers.

## Routing and state

`App.tsx` registers the route map and fallback. `route-map.ts` supplies unavailable shells. `NavigationFocus.tsx` updates the title and focuses the main landmark after path navigation. It preserves initial page focus and native history behavior. Hashes never enter document titles.

Local React state owns input and async outcome. A ref owns the pending request and prevents duplicate submission before a React rerender. The feature aborts its request on unmount and rejects late updates. A new input removes its previous result. No global store, server cache, or duplicated response owner exists.

Future search, filters, sort, pagination, and analytics ranges belong in router query parameters when shareable. Passwords and one-time tokens do not. Feature state owns transient form values. A future session owner owns account identity and lifecycle. Server results need one owner per query, with explicit refresh and invalidation after confirmed mutation.

## API transport and contracts

`client.ts` owns `fetch`, optional Bearer attachment, JSON bodies, a ten-second timeout, cancellation, empty 202/204 handling, and error translation. Credentials default to `omit`. HTTP redirects are rejected. No automatic retry occurs, including after token expiry.

The transport returns `unknown`. `contracts.ts` records current creation fields separately from `CreatedLink`. `adapters.ts` validates object shape, HTTP(S) URLs, public-code consistency, required timestamps, and nullable expiry. `live.ts` translates `expiresAt` to `expires_at` and calls the implemented creation endpoint. Presentation receives only the stable model.

Domain envelopes contain `error` and `message`. FastAPI errors contain string `detail` or validation arrays. `errors.ts` retains their distinct envelope classification, status, safe machine code, safe field mapping, and validated `Retry-After` seconds. It never displays raw server messages or Pydantic `input`. Known domain codes map to controlled feedback. Unknown errors use safe status feedback.

Retry-After supports the backend's integer seconds contract. Accept positive safe integers up to 86400. Invalid or unavailable values use generic waiting guidance. HTTP-date Retry-After is not the current backend contract. If that changes, extend and test the parser before adoption.

Timeout, network error, malformed success, or server error after a mutation can leave its outcome unknown. The feature warns that the link may exist. It does not automatically resubmit. Pre-aborted requests do not dispatch. Cancellation of an obsolete read produces no stale success. Expected HTTP rejection remains distinct from correctness defects.

### Snowflake IDs

Current URL and public-user schemas serialize Python `int` IDs as JSON numbers. JavaScript cannot safely represent every Snowflake value. String conversion after `JSON.parse` cannot recover precision.

Creation returns the URL row ID, not an owner ID. Ownership is absent from this response. The current adapter sets `linkId` to `null` for an unsafe number. It retains public URL creation data, which does not need the numeric link identifier. It never reconstructs an ID from a short code. Safe numeric values can become strings, but this does not establish a lossless general transport contract.

Owner integration is blocked until the backend supplies a documented lossless ID encoding, preferably decimal strings in public schemas and examples. Changing that contract needs backend authorization. Avoid a custom JSON parser across every account response when the source contract can express strings directly.

## Data source and configuration

`readConfig` defaults to live data. `.env.fixture` explicitly selects development fixtures through `npm run dev`. `.env.live` selects HTTP through `npm run dev:live`. Invalid source values fail startup. Every build rejects fixture configuration. Runtime production selection also refuses it.

`createLinkGateway` selects once at bootstrap. Vite's `DEV` branch dynamically imports the sole fixture gateway. Production removes that branch and fixture chunk. A failed live request never selects a fixture. The source label stays visible in the app shell and in demo results.

Fixtures are deterministic, ephemeral, and use the reserved `.invalid` domain. They do not simulate persistence, redirects, accounts, email, or analytics. No MSW, interception library, or second fixture system is installed. Future fixture scenarios must extend this boundary, with visible provenance.

API base configuration permits `/api/v1` or a secure full URL ending in `/api/v1`. It rejects embedded credentials, query values, and fragments. HTTP loopback URLs are allowed only during development. All `VITE_` values are public. Development proxy configuration is server-only and does not settle production origins.

## Authentication and privacy

The transport has an explicit optional access-token seam. No component reads localStorage, sessionStorage, cookies, or JWT claims. No refresh or credential persistence exists. Live guest creation omits auth. An authenticated failure must never retry creation as a guest.

Backend local auth is implemented, including single-use refresh rotation and family revocation on replay. A future live session must use one refresh coordinator. Concurrent 401 handlers must await one rotation. Cross-tab behavior requires a documented ownership/binding strategy before implementation. Do not replay an uncertain mutation after refresh.

Evaluate a same-origin backend-for-frontend or HttpOnly cookie session against in-memory access/refresh credentials. Cookies require server changes, CSRF controls, expiry, logout, and rotation policy. Memory avoids persistent browser storage but loses sessions on reload and still faces script execution risk. Long-lived localStorage refresh credentials are rejected as the default. This comparison does not approve a delivery strategy. The cross-stack session decision remains unresolved.

Google OIDC has no mounted start/callback routes. Browser binding, secure callback delivery, and session handoff remain backend decisions. Do not fake sign-in, embed client secrets, or invent query-token redirects.

Email links currently use `/verify-email#token=...` and `/reset-password#token=...`. The scaffold routes are unavailable. Bootstrap uses the router's path matching to remove and discard their fragments before rendering, including equivalent case, encoding, and trailing-slash forms. It does not consume tokens or claim verification. Later implementation must capture once in memory, remove the fragment immediately, submit only on a deliberate action, then discard it after completion. Reload without a retained credential requires a new link.

Do not persist or log URLs, passwords, tokens, private analytics, or raw HTTP payloads. No analytics SDK, third-party font request, or telemetry exists. The HTML uses `no-referrer` and `noindex,nofollow` for this early preview. Public indexing and production security headers need deployment review.

## Errors, dependencies, and extension rules

The app render boundary supplies a safe reload path. Bootstrap configuration/gateway failure produces safe static feedback. Operational errors belong near the form. Do not swallow important errors or convert them to empty data.

Use native platform behavior, the selected shared primitive, small local code, then a new dependency. Each dependency needs a consumer, alternatives, license, cost, accessibility implications, and replacement boundary in the Source Ledger. No state, form, schema, motion, or GPU framework is required by this scaffold.

Keep simple routes eager. There is no heavy feature to split yet. Future dashboard/analytics owners should load by route when their bundle cost justifies it. Heavy visual systems must remain optional and isolated. Do not add artificial chunks to improve a diagram.

No generated API code exists. Backend imports require settings and unfinished test work, so this scaffold records a bounded creation contract from source. If generation is later selected, generate from an inspected OpenAPI snapshot, record its revision, and do not hand-edit generated outputs. Types never replace runtime validation.

The root [main.py](../../backend/app/main.py) has no SPA hosting or CORS policy. Production requires a separate routing decision. Prefer evaluating same-origin `/api` proxying to avoid unnecessary cross-origin credentials. Reserve SPA routes and API routes separately from public short-code lookup. Current alias reservations do not cover every planned frontend path.

Root Graphify output remains unchanged because this task permits only frontend writes. A later authorized graph update must refresh the new modules.
