# Frontend workflows

**Owner:** User-visible frontend behavior

## Availability language

`CURRENT` means observed implementation at its stated boundary. `FRONTEND_FIXTURE_ONLY` means deterministic browser presentation without real persistence. `BLOCKED_BACKEND` means a necessary endpoint is absent. `PLANNED` means accepted work without implementation evidence. `DEFERRED` means deliberately postponed.

Backend implementation is a separate dimension. A mounted auth endpoint does not make its frontend page complete. Fixture results do not establish live database, Redis, email, or redirect behavior.

## Route map

| Frontend path                   | Current behavior                                                     | Workflow classification                                                              |
| ------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `/`                             | Destination input, explicit data-source banner, guest preview/result | `FRONTEND_FIXTURE_ONLY` by default. HTTP adapter exists, live integration unverified |
| `/login`                        | Unavailable sign-in shell                                            | `PLANNED`. Live session integration blocked by contract                              |
| `/register`                     | Unavailable registration shell                                       | `PLANNED`. Backend local registration exists                                         |
| `/verify-email`                 | Unavailable verification shell. Fragment removed and discarded       | `PLANNED`. Backend token consumption exists                                          |
| `/forgot-password`              | Unavailable recovery shell                                           | `PLANNED`. Backend accepts requests                                                  |
| `/reset-password`               | Unavailable reset shell. Fragment removed and discarded              | `PLANNED`. Backend reset exists                                                      |
| `/dashboard`                    | Unavailable saved-links shell                                        | `BLOCKED_BACKEND` for live listing                                                   |
| `/dashboard/urls/:id`           | Unavailable details shell                                            | `BLOCKED_BACKEND` for live management and lossless IDs                               |
| `/dashboard/urls/:id/analytics` | Unavailable analytics shell                                          | `BLOCKED_BACKEND` for live reports                                                   |
| Unmatched paths                 | Page-not-found shell with home link                                  | `CURRENT` browser routing                                                            |

These frontend owner routes are presentation paths, not new backend endpoint promises. Browser history requires SPA fallback in production. Public `/{short_code}` belongs to the backend redirect service on the selected public origin. Hosting precedence remains unresolved.

## Guest creation and generated result

Guest creation is first-class. Never force login before shortening. The scaffold currently accepts a destination only. The next guest task adds alias, expiry, complete field validation, and recovery.

1. Enter an HTTP(S) URL.
2. Submit once. The form keeps the destination visible and disables duplicate submission.
3. In fixture mode, show a labeled demo URL on `.invalid`. Save nothing and do not navigate to it.
4. In live mode, use returned public URL data after adapter checks. Do not invent a host or claim working redirects.
5. Select the read-only result to copy manually. Dedicated clipboard and QR actions remain planned.

No creation failure becomes success or confirmed empty. Preserve input on conflict, validation, limiting, or service failure. State includes idle, loading, ready, and error. Feedback identifies uncertain mutation outcomes separately. Invalid user input uses native validation in this minimal slice. Full adjacent field errors remain in the next task.

Planned copy must await `navigator.clipboard.writeText`. Denial needs explicit manual recovery. Planned QR uses the actual public code endpoint only after its response contract exists. Fixture QR, if later added, must stay labeled and must not claim backend generation.

## Local account and recovery journeys

The target journey is register, request/receive email, verify, then sign in. Backend register/login/verify/me routes exist. Local password requests enforce 12–128 characters. Frontend account forms remain planned.

Registration can persist an account before provider delivery fails. Do not promise that a generic error means no account exists. Recovery needs a documented resend/provider-outage contract. Empty forgot-password and resend `202` confirms acceptance, not account existence or delivery.

Reset uses an email-link fragment, deliberate submission, and safe empty `204` handling. Single-use/expired tokens need a replacement-link path. Password reset invalidates access through `auth_version` and revokes refresh families. Logout revokes refresh families, but a still-valid access token can remain valid until expiry. Do not promise stronger immediate backend invalidation.

Google sign-in remains `BLOCKED_BACKEND`. No enabled Google control or fake success exists. Future account shells can use development fixtures without issuing production credentials, but that provider requires its own implementation and explicit label.

## Protected navigation, dashboard, and analytics

The scaffold displays unavailable shells before any account data fetch. It has no guessed route guard or fake authenticated user. Future guards need session states: unknown/loading, guest, authenticated, expired, and unavailable. Preserve a local return path, never an unvalidated external redirect.

A route guard improves navigation but does not authorize data. The backend must enforce owner access. Do not map failed listing to zero links or failed analytics to zero clicks. Distinguish loading, confirmed empty, error, blocked, partial, and stale when those states have evidence.

Future dashboard filters and pagination belong in the URL. Refresh only after a confirmed mutation and invalidate the affected owner list/detail. Reject late responses for another resource or account. Clear private state on logout/account change. Analytics must show timezone, range, units, and data freshness. Charts need a text summary or accessible table.

## Navigation and recovery

Navigation preserves logical order and visible focus. Path changes focus the main landmark and update a safe title. The skip link targets the main landmark. The fallback supplies a real home link. Reload preserves known paths under the development server.

A request abort on navigation prevents stale React updates. It does not prove that a dispatched mutation never reached the backend. No automatic retry or fixture fallback occurs. Render failure uses a safe reload link. Broken bootstrap configuration uses explicit safe feedback.

## Deferred behavior

Dark mode, smooth-scroll controllers, GPU decoration, themes, team workspaces, custom domains, bulk actions, and API keys remain `DEFERRED`. Landing polish is `PLANNED`. Their absence does not block independent guest UI work.
