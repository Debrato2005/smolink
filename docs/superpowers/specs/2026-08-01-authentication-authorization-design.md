# Production authentication and authorization design

**Status:** approved target design; partially implemented (local login/JWT foundation)
**Date:** 2026-08-01

## Purpose and scope

Define Smolink's complete local-password and Google OIDC authentication system.
It supersedes the earlier minimal-auth checklist item, while preserving optional
authentication for URL creation. It does not add roles, organizations, API keys,
custom domains, or external identity providers beyond Google.

## Implementation status (2026-08-04)

Implemented: registration and local-login foundations, Argon2id password
verification, five-failure/15-minute account locking, signed access/refresh
JWT helpers, keyed refresh-JTI storage, and shared registration/login IP
limiting. Focused API verification is still in progress. Refresh rotation,
logout, email verification and reset flows, bearer-token dependencies, and
Google OIDC are not yet implemented.

## Product decisions

- Emails are normalized with `strip().lower()` before lookup and persistence.
- New password registrations are **blocked from login** until email verification
  succeeds. This is the explicit product decision for v1.
- Google accounts are considered verified only after validating Google's OIDC
  ID token and `email_verified` claim.
- A verified Google email matching a local account auto-links the Google
  identity to that existing user. It never creates a second user for that email.
- Login failures receive a generic invalid-credentials response to avoid account
  enumeration. Registration still returns `409` for an existing email.
- Access and refresh tokens are JWTs, but refresh lifecycle state is durable in
  Postgres so rotation, logout, reset, and reuse detection are enforceable.

## API contract

All domain errors use the project envelope:

```json
{"error":"machine_code","message":"human readable message"}
```

| Method | Path | Request / response | Main outcomes |
|---|---|---|---|
| POST | `/api/v1/auth/register` | `{email,password}` → public user | `201`, `409 email_taken`, `422` |
| POST | `/api/v1/auth/login` | `{email,password}` → token pair | `200`, `401 invalid_credentials`, `403 email_unverified`, `423 account_locked`, `429`, `503` |
| POST | `/api/v1/auth/refresh` | `{refresh_token}` → rotated token pair | `200`, `401 invalid_refresh_token` |
| POST | `/api/v1/auth/logout` | authenticated refresh token/session reference | `204` |
| GET | `/api/v1/auth/me` | Bearer access token → public user | `200`, `401` |
| POST | `/api/v1/auth/verify-email` | `{token}` → public user | `200`, `400 invalid_or_expired_token` |
| POST | `/api/v1/auth/forgot-password` | `{email}` → empty response | always `202` |
| POST | `/api/v1/auth/reset-password` | `{token,new_password}` | `204`, `400 invalid_or_expired_token`, `422` |
| GET | `/api/v1/auth/google/start` | redirect to Google | `302` |
| GET | `/api/v1/auth/google/callback` | authorization response → Smolink token pair | `302` to trusted frontend callback or documented JSON error |

The token-pair response is:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 900
}
```

Passwords are never returned, logged, placed in JWTs, or included in error
messages. The public user response contains only `id`, `email`,
`email_verified_at`, `created_at`, and `updated_at`.

## Persistence model

Extend the initial model through a new Alembic migration; do not modify the
applied initial migration.

| Table | Durable responsibility |
|---|---|
| `users` | Normalized unique email, nullable Argon2id hash (Google-only users have none), `email_verified_at`, failed-login count, `locked_until`, and `auth_version`. |
| `auth_identities` | One provider subject (`provider`, `provider_subject`) linked to one user; unique on provider/subject and indexed by user. |
| `refresh_tokens` | Hash of refresh JWT `jti`, user, token-family UUID, parent token, issued/used/revoked/expiry timestamps, and optional audit metadata. |
| `email_verification_tokens` | Hashed opaque token, user, expiry, consumed timestamp. |
| `password_reset_tokens` | Hashed opaque token, user, expiry, consumed timestamp. |
| `oauth_authorization_requests` | Hashed `state`, nonce, PKCE verifier, expiry, and consumed timestamp for one Google authorization attempt. |

All lookup tokens are random, high-entropy, one-time values stored as keyed
hashes; raw verification and reset tokens are delivered only to the user. A
password reset increments `auth_version`, revokes every active refresh-token
family for that user, and consumes the reset token atomically.

## Modules and boundaries

Add an `auth` domain without moving unrelated URL code:

```text
backend/app/
├── api/v1/endpoints/auth.py       # HTTP translation only
├── api/v1/dependencies/auth.py    # OAuth2PasswordBearer and current-user deps
├── models/auth_*.py               # durable auth tables
├── repositories/auth_repository.py
├── schemas/auth.py
├── services/auth_service.py        # local auth, tokens, verification, reset
├── services/google_oidc_service.py # authorization-code/OIDC validation
└── utils/security.py               # Argon2id, JWT, random-token helpers
```

Routes do not query SQL directly. Services coordinate policy and repositories;
repositories own SQL. One shared `SnowflakeGenerator` configuration supplies
user and auth-record IDs; never instantiate a generator per request.

## Security model

- Use Argon2id through `argon2-cffi`; verification is the library's
  constant-time operation. Enforce passwords of 12–128 characters.
- Use `OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")` for access-token
  extraction. `get_current_user()` validates the token and loads an enabled,
  verified user; `get_optional_current_user()` returns `None` only when no
  credential is supplied.
- Access JWT default TTL: 15 minutes. Refresh JWT default TTL: 30 days. Both
  are configurable and validate `iss`, `aud`, `exp`, `nbf`, `typ`, and `jti`.
  Access JWTs also carry `sub` and `auth_version`; refresh JWTs carry `sub`,
  `jti`, and family ID. Do not put email, password state, or permissions in a
  token.
- Configure JWT issuer, audience, signing secret, access/refresh TTLs, token
  hash secret, Google client ID/secret, Google redirect URI, and email sender
  settings exclusively through environment-backed settings. Production secrets
  are distinct, high-entropy values and are never committed.
- Apply the existing five-per-IP rolling-minute limiter to registration, login,
  refresh, reset, verification, and Google callback writes. Redis outages fail
  closed with `503` on these protected writes.
- Persist per-account password failures. After five consecutive failures,
  lock the account for 15 minutes; successful login resets the counter. A
  locked account returns `423` without checking the password.
- Refresh rotation consumes the presented record and creates a child token in
  the same family in one transaction. A consumed token presented again revokes
  every token in that family and returns `401`.

## Google OAuth2/OpenID Connect flow

1. `/google/start` creates a one-time authorization request with random state,
   nonce, PKCE verifier, and ten-minute expiry, then redirects to Google using
   authorization-code flow.
2. `/google/callback` matches and consumes state, exchanges the code, obtains
   Google's discovery metadata/JWKs, and validates ID-token signature, issuer,
   audience, expiry, nonce, subject, and verified email.
3. The service finds `auth_identities(provider="google", subject)`. If absent,
   it finds the normalized verified email: link that user if found, otherwise
   create a verified Google-only user and identity.
4. The service issues Smolink's own token pair. Google access/ID tokens are
   never treated as Smolink API credentials or stored as reusable sessions.

## Email and reset flow

Registration commits a user and one verification record, then dispatches email
after the transaction boundary. Verification atomically consumes the record and
sets `email_verified_at`. Forgot-password always returns `202`; only a matching
eligible local account receives a reset email. Reset consumes the record,
changes the Argon2id hash, clears lock state, increments `auth_version`, and
revokes refresh families in one transaction.

## Tests and verification

Unit-test password/JWT helpers, normalization, token claims, lock policy,
rotation, and Google-claim validation. Integration/API tests must cover:

- registration, duplicate normalized email, unverified-login block, verified
  login, invalid credentials, IP limit, account lock and successful-login reset;
- missing, malformed, expired, wrong-issuer/audience, revoked, and
  auth-version-invalid access tokens; protected and optional-auth dependencies;
- refresh rotation, expired/revoked refresh tokens, reuse detection, family
  revocation, logout, and password-reset session invalidation;
- one-time/expired verification and reset tokens, plus non-enumerating forgot
  password responses;
- Google state/nonce/PKCE and ID-token validation, new user creation, and
  verified-email auto-linking; and
- Postgres/Redis/email/Google-provider outage contracts without leaking secrets.

Run focused auth tests and then `uv run pytest -q -s`. Verify the migration
against Compose Postgres before marking the checklist complete.

## References

- [OAuth 2.0 Security Best Current Practice (RFC 9700)](https://www.rfc-editor.org/rfc/rfc9700.html)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [FastAPI OAuth2PasswordBearer documentation](https://fastapi.tiangolo.com/tutorial/security/first-steps/)
