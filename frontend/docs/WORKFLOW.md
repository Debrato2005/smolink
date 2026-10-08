# Frontend workflows

**Owner:** User-visible frontend behavior

## Availability language

`CURRENT` means observed implementation at its stated boundary. `FRONTEND_FIXTURE_ONLY` means deterministic browser presentation without real persistence. `BLOCKED_BACKEND` means a necessary endpoint is absent. `PLANNED` means accepted work without implementation evidence. `DEFERRED` means deliberately postponed.

Backend implementation is a separate dimension. A mounted auth endpoint does not make its frontend page complete. Fixture results do not establish live database, Redis, email, or redirect behavior.

## Route map

Fixture mode (`npm run dev`) shows every journey with local development data that looks like the real product. A development-only Developer tools panel in the footer names that data and switches scenarios. Live mode (`npm run dev:live` and production) connects guest creation only and marks other features as coming soon. No product copy says demo or sample.

| Frontend path                              | Fixture behavior                                                 | Live behavior                                              | Classification                                                   |
| ------------------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------- |
| `/`                                        | Shortener, result ticket, QR preview, features, steps, questions | Real `POST /api/v1/urls`. QR button disabled               | Live HTTP adapter exists. Real-stack journey unverified          |
| `/login`, `/register`                      | Email forms, Continue with Google, development-only test account | Google and email disabled under "Accounts are coming soon" | `FRONTEND_FIXTURE_ONLY`. Live session `BLOCKED_BACKEND` contract |
| `/verify-email`, `/reset-password`         | Fragment captured in memory and removed. Simulated submission    | Fragment removed. Forms disabled                           | `FRONTEND_FIXTURE_ONLY`                                          |
| `/forgot-password`, `/resend-verification` | Simulated acceptance with delivery caveat                        | Forms disabled                                             | `FRONTEND_FIXTURE_ONLY`                                          |
| `/dashboard`                               | Link list, search, status filter, sort, pagination in the URL    | "Your workspace is on its way" coming-soon state           | Live listing `BLOCKED_BACKEND`                                   |
| `/dashboard/new`                           | Bench inside the workspace                                       | Unavailable state                                          | `FRONTEND_FIXTURE_ONLY`                                          |
| `/dashboard/urls/:id`                      | Ticket summary, edit, pause, confirmed delete                    | Unavailable state                                          | Live management `BLOCKED_BACKEND`, lossless IDs blocked          |
| `/dashboard/urls/:id/analytics`            | 7 or 30 days, chart, tables, UTC freshness                       | Unavailable state                                          | Live reports `BLOCKED_BACKEND`                                   |
| Unmatched paths                            | Page-not-found with a home link                                  | Same                                                       | `CURRENT`                                                        |

These are presentation paths, not backend endpoint promises. Production needs an SPA fallback. Public `/{short_code}` belongs to the backend redirect service. Hosting precedence remains unresolved.

## Guest creation and generated result

Guest creation is first-class. Never force login before shortening.

1. Paste an `http://` or `https://` URL.
2. Optionally enter an alias (3–64 letters, numbers, or hyphens, saved in lowercase) and an expiry in the local timezone.
3. Submit once. The form disables duplicate submission and keeps every value.
4. Fixture mode returns a URL on the reserved `smolink.test` domain. Live mode uses the returned public URL after adapter checks and adds one line: short links start redirecting when the redirect service launches.
5. The result ticket appears below the form and shows the short URL, the before and after length, and the expiry. Its short URL receives focus and selects its text. The browser brings the URL into view only when needed. If an alias makes the link longer, the ticket says so.
6. Copy awaits `navigator.clipboard.writeText`. Denial shows a selectable manual-copy field. QR preview exists in fixture mode only.

Field errors appear next to their fields. Conflicts (`409`), validation (`422`), limits (`429` with wait seconds), and service failures (`503`) use explicit text. A failure after dispatch warns that the link may exist. No failure becomes success, and no fixture replaces a live failure.

## Local account and recovery journeys

The target journey is register, request/receive email, verify, then sign in. Backend register/login/verify/me routes exist. Local password requests enforce 12–128 characters. Frontend account forms work with local development data. Live session and recovery integration remain blocked.

Registration can persist an account before provider delivery fails. Do not promise that a generic error means no account exists. Recovery needs a documented resend/provider-outage contract. Empty forgot-password and resend `202` confirms acceptance, not account existence or delivery.

Reset uses an email-link fragment, deliberate submission, and safe empty `204` handling. Single-use/expired tokens need a replacement-link path. Password reset invalidates access through `auth_version` and revokes refresh families. Logout revokes refresh families, but a still-valid access token can remain valid until expiry. Do not promise stronger immediate backend invalidation.

Google sign-in is `BLOCKED_BACKEND` for live use. The **Continue with Google** button appears on sign-in and registration. In production it is disabled under the coming-soon notice. With development data it calls the fixture gateway's `google` account action, which never contacts Google and issues no credential. A live flow needs the backend start and callback routes and a settled session contract.

## Protected navigation, dashboard, and analytics

Live mode displays an unavailable state before any account data fetch. Fixture mode uses an in-memory development identity. **Use test account**, email sign-in, or the Google fixture action sets it. **Sign out** or reload clears it. No credential is stored. Without the development identity, workspace routes show a sign-in prompt with a validated local return path. Future guards need session states: unknown/loading, guest, authenticated, expired, and unavailable. Preserve a local return path, never an unvalidated external redirect.

A route guard improves navigation but does not authorize data. The backend must enforce owner access. Do not map failed listing to zero links or failed analytics to zero clicks. Distinguish loading, confirmed empty, error, blocked, partial, and stale when those states have evidence.

Dashboard filters, sorting, and pagination use the URL. Refresh only after a confirmed mutation and invalidate the affected owner list/detail. Reject late responses for another resource or account. Clear private state on logout/account change. Analytics must show timezone, range, units, and data freshness. The chart exposes a text summary and the Daily clicks table. Its heading wraps at narrow widths. Count and date labels wrap within their columns, including at 320px with extra text spacing. The daily table remains keyboard-scrollable. These are fixture reports, not live analytics.

## Navigation and recovery

Navigation preserves logical order and visible focus. Path changes focus the main landmark and update a safe title. The skip link targets the main landmark. The fallback supplies a real home link. Reload preserves known paths under the development server.

A request abort on navigation prevents stale React updates. It does not prove that a dispatched mutation never reached the backend. No automatic retry or fixture fallback occurs. Render failure uses a safe reload link. Broken bootstrap configuration uses explicit safe feedback.

Boxed blocks use a small hover lift on pointer devices. Reduced motion and touch-only pointers keep blocks stationary. Informational cards retain their normal cursor and semantics.

## Deferred behavior

Dark mode, smooth-scroll controllers, GPU decoration, themes, team workspaces, custom domains, bulk actions, and API keys remain `DEFERRED`. The landing redesign works in Chromium. Firefox, WebKit, and physical-device review remain open. Their absence does not block independent guest UI work.
