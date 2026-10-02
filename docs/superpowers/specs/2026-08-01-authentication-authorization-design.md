# Authentication and authorization design

**Status:** approved target. Local flows are implemented. Google OIDC remains pending.
**Design date:** 2026-08-01

## Scope and implementation status

This design replaces the earlier minimal-auth milestone. It preserves optional
authentication for URL creation. It does not add roles, organizations, API keys,
custom domains, or providers other than Google.

Use the [walkthrough](../../codebase-walkthrough.md#local-authentication) for
implemented behavior and the [checklist](../../backend-build-checklist.md#current-verified-state)
for verification evidence. The contract below is the target. Current error
normalization, generator sharing, and Google sign-in remain incomplete.

## Product decisions

- Normalize email with `strip().lower()` before lookup and persistence.
- Block new password accounts from login until email verification succeeds.
- Accept Google verification only after ID-token validation and a verified-email claim.
- Link a verified Google email to the matching local account instead of creating a second user.
- Return generic invalid credentials for login failures. Duplicate registration still returns `409`.
- Persist refresh lifecycle state in PostgreSQL for rotation, logout, reset, and reuse detection.

JSON Web Token (JWT) access credentials carry identity and validation claims.
They do not replace current-user lookup or durable refresh state.
OpenID Connect (OIDC) supplies the planned Google identity flow.

## API contract

Domain errors use:

```json
{"error":"machine_code","message":"human readable message"}
```

Current FastAPI validation and dependency errors still use `detail`.
A shared error schema and global domain handlers remain targets.
Request-validation normalization remains a release requirement.

| Method | Path | Request / response | Main domain outcomes | Status |
|---|---|---|---|---|
| POST | `/api/v1/auth/register` | `{email,password}` → public user | `201`, `409 email_taken`, `422` | Implemented |
| POST | `/api/v1/auth/login` | `{email,password}` → token pair | `200`, `401 invalid_credentials`, `403 email_unverified`, `423 account_locked` | Implemented |
| POST | `/api/v1/auth/refresh` | `{refresh_token}` → rotated pair | `200`, `401 invalid_refresh_token` | Implemented |
| POST | `/api/v1/auth/logout` | `{refresh_token}` | `204`, `401 invalid_refresh_token` | Implemented |
| GET | `/api/v1/auth/me` | Bearer access token → public user | `200`, `401` | Implemented |
| POST | `/api/v1/auth/verify-email` | `{token}` → public user | `200`, `400 invalid_or_expired_token` | Implemented |
| POST | `/api/v1/auth/resend-verification` | `{email}` → empty body | `202` across account states | Implemented |
| POST | `/api/v1/auth/forgot-password` | `{email}` → empty body | `202` across account states | Implemented |
| POST | `/api/v1/auth/reset-password` | `{token,new_password}` | `204`, `400 invalid_or_expired_token`, `422` | Implemented |
| GET | `/api/v1/auth/google/start` | Redirect to Google | `302` | Planned |
| GET | `/api/v1/auth/google/callback` | Google response → Smolink authentication | Trusted frontend redirect or documented JSON error. Delivery details unresolved | Planned |

All implemented auth POST routes share the IP limiter. Validation, limiter
rejection (`429`), limiter failure (`503`), and database failures can occur
before a successful domain response. `202` consistency concerns account state.
It is not a guarantee across all failures.

The token-pair response is:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 900
}
```

`expires_in` reflects configured access-token lifetime. `900` is the template
value. Public users contain only `id`, `email`, `email_verified_at`,
`created_at`, and `updated_at`. Never return or log passwords or put them in JWTs.

## Persistence

Use new Alembic revisions for schema changes. Preserve applied migration history.
The auth tables and user fields exist:

| Table | Responsibility |
|---|---|
| `users` | Normalized unique email, nullable Argon2id hash, verification time, failure count, lock time, and `auth_version` |
| `auth_identities` | Unique provider/subject pair linked to a user and indexed by user |
| `refresh_tokens` | Keyed refresh `jti` hash, user, family UUID, parent, and issued/expiry/use/revocation times |
| `email_verification_tokens` | Hashed opaque value, user, expiry, consumption time |
| `password_reset_tokens` | Hashed opaque value, user, expiry, consumption time |
| `oauth_authorization_requests` | Hashed state, nonce, raw PKCE verifier, expiry, consumption time |

Opaque verification and reset values are random, single-use, and stored as
keyed hashes. Refresh JWTs are signed. Their `jti` is hashed for database lookup.
OAuth nonce and PKCE verifier fields are not hashed by the current model.
Keep the verifier secret. The table alone does not implement callback validation.
The original target also allows optional refresh audit metadata. The current
`RefreshToken` model has no audit-metadata field.

Password reset atomically consumes its record, replaces the password, clears
lock state, increments `auth_version`, and revokes every active refresh family.

## Modules and boundaries

Use the shared layer layout:

```text
backend/app/
├── api/v1/endpoints/auth.py
├── api/v1/dependencies/auth.py
├── models/                        # auth and URL tables
├── repositories/auth_repository.py
├── repositories/user_repository.py
├── schemas/auth.py
├── services/auth_service.py
├── services/email_service.py
├── services/google_oidc_service.py # planned
└── utils/security.py
```

Routes translate HTTP and commit workflows. Services coordinate policy through
a shared session. Repositories own SQL and flush without commit.
The target shares one `SnowflakeGenerator` sequence where a worker ID is shared.
Current auth and URL routes instead create independent generators. Coordinate
these before claiming collision-free IDs across both workflows.

## Local security rules

- Use Argon2id through `argon2-cffi` for hashing and library-backed password checks.
- Enforce 12–128 characters for local registration, login, and replacement passwords.
- Use `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` to extract access tokens.
- Load the current user and check verification and `auth_version` after JWT validation.
- For the approved optional-auth target, return `None` only when no credential is supplied. Reject invalid supplied credentials.
- Validate `iss`, `aud`, `exp`, `nbf`, `typ`, and `jti`. Require `sub` and the token-specific claims.
- Keep email, password state, and permissions out of JWTs.
- Configure secrets, issuer, audience, lifetimes, Google credentials, redirect URI, and email settings through environment-backed settings.
- Keep production secrets distinct and uncommitted.

Current optional extraction treats absent or non-Bearer authorization as guest
access. An invalid supplied Bearer token returns `401`. The non-Bearer behavior
differs from the stricter approved target and remains an implementation gap.

The environment template sets access lifetime to 15 minutes and refresh
lifetime to 30 days. Both fields are required settings, not Python defaults.
Rotation gives each refresh token a new expiry. The current code does not
impose an absolute 30-day family lifetime.

Persist password failures per account. At five consecutive failures, set a
15-minute lock. A locked account returns `423` before password verification.
Successful verified login clears failure state. The shared Redis limit allows
five auth writes per IP per rolling minute. Limiter failure returns `503`.
The planned Google callback must also apply this policy.

Refresh rotation locks and consumes the presented record, then creates a child
in one transaction. Reuse revokes the family and returns `401`. Commit that
revocation even when the route returns an error. Logout blocks future refreshes.
It does not revoke a still-valid access JWT. Password reset does so through
`auth_version`.

## Google authorization target

Google routes remain unimplemented. The target uses an authorization code,
state, nonce, and PKCE (Proof Key for Code Exchange).

1. Create a one-time authorization request with random state, nonce, a secret verifier, and a ten-minute expiry.
2. Bind the request to the initiating browser session.
3. Redirect the browser to Google with state, nonce, and the S256 challenge.
4. On callback, check the browser binding, state, expiry, and prior consumption.
5. Consume the matching authorization request.
6. Exchange the code with the verifier at Google's token endpoint.
7. Load Google's discovery metadata and JSON Web Keys (JWKs).
8. Validate ID-token signature, issuer, audience, expiry, nonce, subject, and verified email.
9. Find the provider identity by `provider="google"` and `provider_subject`.
10. If the identity is absent, link a matching normalized verified email or create a verified Google-only account.
11. Issue Smolink's token pair through the approved frontend delivery contract.

The S256 challenge is Base64url of SHA-256 of the ASCII verifier, without
padding. The challenge is public. Possession of a valid code alone does not
replace possession of the verifier. See [RFC 7636](https://www.rfc-editor.org/rfc/rfc7636.html#section-4.2).

State must correlate the callback with the browser that started authorization.
Nonce binds the ID token to the authentication request. Google tokens are not
Smolink API credentials or reusable Smolink sessions. Browser-binding transport
and final token delivery remain unresolved. A stored state hash alone does
not define either contract. These requirements follow the
[OAuth security guidance](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.7).

## Email and reset behavior

Registration commits the user and verification record before sending email.
Verification consumes its record and sets `email_verified_at` in one transaction.
Verification tokens expire after 24 hours. Reset tokens expire after one hour.

Forgot-password creates a reset record only for a matching password account.
Resend verification consumes prior unused records only for an eligible
unverified password account, then creates one replacement. Unknown, verified,
and passwordless accounts receive the same empty `202` account-state response.
Both routes commit before delivery and suppress `EmailDeliveryError`.
Registration instead lets delivery failure propagate after commit.
A complete provider-outage contract remains release work.

Raw opaque tokens appear in email-link fragments, not API responses or database
rows. The sender URL-encodes the token and HTML-escapes the link.

## Verification procedure

Prerequisites: configured local PostgreSQL and Redis, the reviewed migration
chain, and sender/provider test doubles. Run commands from `backend/`.
Use the [development guide](../../development.md) for setup.

1. Run the focused API tests:

   ```bash
   uv run pytest tests/test_auth.py -q -s
   ```

2. Run the full suite:

   ```bash
   uv run pytest -q -s
   ```

3. Test the migration chain against a separate empty development database.
4. Record successful verification before marking the milestone complete.

Coverage must include local password/JWT helpers, normalization, lock policy,
rotation, and eventual Google validation. API/integration cases include:

- Registration, duplicate email, verification requirement, credentials, limits, locking, and successful-login state reset.
- Missing, malformed, expired, wrong-issuer/audience, and auth-version-invalid access tokens. Include required and optional authentication.
- Refresh expiry, revocation, rotation, reuse, logout, and reset invalidation.
- Single-use and expired opaque tokens. Include account-state-consistent forgot-password and resend responses.
- Google browser binding, state, nonce, PKCE, ID-token validation, new accounts, and verified-email linking.
- PostgreSQL, Redis, email, and Google failures without exposing secrets.

## Open implementation contracts

- Global error normalization is incomplete. Validation and dependency failures still use `detail`.
- Optional authentication accepts non-Bearer authorization as guest access. The approved target permits guest access only when no credential is supplied.
- Google browser binding and frontend token delivery need an explicit design before implementation.
- Registration persists before email delivery. Provider failure recovery is not yet specified.
- Generator instances need coordinated sequence state when they share a worker ID.
- OIDC helper and route work is unfinished. Existing tables are not proof of working sign-in.

## References

- [OAuth 2.0 Security Best Current Practice (RFC 9700)](https://www.rfc-editor.org/rfc/rfc9700.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [Proof Key for Code Exchange (RFC 7636)](https://www.rfc-editor.org/rfc/rfc7636.html)
- [FastAPI OAuth2PasswordBearer documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/)
