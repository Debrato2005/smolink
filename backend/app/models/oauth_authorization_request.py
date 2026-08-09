from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OAuthAuthorizationRequest(Base):
    __tablename__ = "oauth_authorization_requests"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
    )
    state_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )
    nonce: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    pkce_verifier: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


# ===============================================================================
# OAUTH 2.0 + OPENID CONNECT — HOW IT WORKS AND WHAT EACH SECURITY MECHANISM
# PREVENTS
# ===============================================================================

# Example:
#     User = Alice
#     Application = Smolink
#     Identity Provider = Google

# The goal is:

#     Alice wants to log into Smolink using her Google account.

# ===============================================================================
# 1. USER STARTS LOGIN
# ===============================================================================

# Alice clicks:

#     "Continue with Google"

# Smolink creates a temporary OAuth authorization request:

#     state
#     nonce
#     PKCE verifier
#     expiry time

# Smolink stores these server-side.

# Then Smolink redirects Alice's browser to Google with:

#     client_id
#     redirect_uri
#     state
#     nonce
#     PKCE challenge

# Important:

#     verifier  -> kept secret by Smolink
#     challenge -> sent to Google

# ===============================================================================
# 2. GOOGLE AUTHENTICATES ALICE
# ===============================================================================

# Browser
#     ↓
# Google

# Alice enters her Google credentials.

# Google authenticates Alice.

# Google then generates a temporary:

#     Authorization Code

# Example:

#     code = ABC123

# Google redirects the browser back to:

#     https://smolink.com/oauth/callback
#         ?code=ABC123
#         &state=XYZ789

# ===============================================================================
# 3. SMOLINK RECEIVES THE CALLBACK
# ===============================================================================

# Smolink receives:

#     authorization_code
#     state

# Smolink finds the OAuth request it created earlier.

# Then it checks:

#     1. Does the returned state match the stored state?
#     2. Has the request expired?
#     3. Has the request already been consumed?

# If any check fails:

#     Reject the request.

# ===============================================================================
# 4. STATE — PREVENTS CSRF / LOGIN CSRF
# ===============================================================================

# ATTACK:

# Bob logs into HIS Google account.

# Google gives Bob:

#     code = BOBS_CODE

# Bob tricks Alice's browser into visiting:

#     /oauth/callback?code=BOBS_CODE

# Without state, Smolink might associate Bob's login with Alice's browser.

# Result:

#     Alice thinks she is using her own account,
#     but she is actually logged into Bob's Smolink account.

# This is Login CSRF.

# PREVENTION:

# Alice's login started with:

#     state = ALICE_RANDOM_VALUE

# Google must return that same state.

# Bob's attack contains:

#     state = BOB_RANDOM_VALUE

# Smolink compares:

#     BOB_RANDOM_VALUE
#             ≠
#     ALICE_RANDOM_VALUE

# Therefore:

#     Reject.

# STATE means:

#     "Does this callback belong to the login flow I started?"

# ===============================================================================
# 5. NONCE — PREVENTS REPLAY / TOKEN MIX-UP
# ===============================================================================

# During the login request, Smolink generates:

#     nonce = RANDOM_VALUE

# Smolink sends the nonce to Google.

# Google puts that nonce into the resulting OpenID Connect ID Token.

# Example ID Token claims:

#     {
#         "sub": "google-user-123",
#         "nonce": "RANDOM_VALUE"
#     }

# Smolink checks:

#     nonce in ID Token
#             =
#     nonce stored for this login

# If they don't match:

#     Reject.

# WHY?

# Suppose an attacker tries to reuse an old ID Token from another
# authentication flow.

# The old token contains:

#     nonce = OLD_VALUE

# The current login expects:

#     nonce = NEW_VALUE

# Therefore:

#     OLD_VALUE ≠ NEW_VALUE

#     → Reject

# NONCE means:

#     "Does this ID Token belong to the authentication request I started?"

# ===============================================================================
# 6. AUTHORIZATION CODE INTERCEPTION
# ===============================================================================

# Another attack is stealing the authorization code.

# Without PKCE:

#     Google
#        ↓
#     Authorization Code
#        ↓
#     Browser

# An attacker intercepts:

#     code = ABC123

# The attacker sends:

#     code = ABC123

# to Google's token endpoint.

# If the code is valid, the attacker may be able to obtain tokens.

# The authorization code itself is therefore not enough protection.

# ===============================================================================
# 7. PKCE — PREVENTS AUTHORIZATION CODE INTERCEPTION
# ===============================================================================

# Smolink generates a secret:

#     PKCE verifier

# Example:

#     verifier = RANDOM_SECRET

# Then derives:

#     challenge = SHA256(verifier)

# Smolink sends ONLY the challenge to Google.

# Google remembers:

#     challenge

# The verifier remains with Smolink.

# Later, after receiving the authorization code, Smolink sends:

#     authorization_code
#     +
#     verifier

# to Google.

# Google calculates:

#     SHA256(verifier)

# and compares it with the challenge from the original request.

# If:

#     SHA256(verifier) == stored_challenge

#     → Accept

# Otherwise:

#     → Reject

# ATTACK:

# Attacker steals:

#     authorization_code

# But attacker does NOT have:

#     PKCE verifier

# Therefore:

#     authorization_code alone
#             ↓
#         Not enough
#             ↓
#         Reject

# PKCE means:

#     "Prove that you possess the secret verifier associated with
#      this authorization request."

# ===============================================================================
# 8. WHY CAN THE ATTACKER STEAL THE CHALLENGE?
# ===============================================================================

# That's okay.

# The challenge is intentionally not secret.

# The important value is:

#     verifier = SECRET

# The relationship is:

#     verifier
#         ↓
#     SHA256
#         ↓
#     challenge

# Knowing:

#     challenge

# does not practically allow the attacker to recover:

#     verifier

# Therefore:

#     Challenge can be exposed.
#     Verifier must remain secret.

# ===============================================================================
# 9. AUTHORIZATION CODE REPLAY
# ===============================================================================

# Suppose the authorization code is used successfully.

# An attacker later tries to use the same code again.

# OAuth authorization codes are intended to be short-lived and single-use.

# The authorization server rejects an already-used or expired code.

# Your application also tracks the OAuth authorization request as consumed:

#     consumed_at = NOW()

# Therefore a second attempt to use the same authorization flow is rejected.

# ===============================================================================
# 10. EXPIRATION
# ===============================================================================

# OAuth authorization requests are temporary.

# Example:

#     Created:
#         10:00

#     Expires:
#         10:05

# If someone tries the callback at:

#     10:20

# Smolink checks:

#     current_time > expires_at

# Therefore:

#     Reject.

# This limits the lifetime of abandoned or stolen OAuth-flow state.

# ===============================================================================
# 11. COMPLETE FLOW
# ===============================================================================

#                     Alice
#                       |
#                       | "Login with Google"
#                       v
#                    Smolink
#                       |
#               Generate:
#               - state
#               - nonce
#               - PKCE verifier
#                       |
#               Store temporarily
#                       |
#               Generate PKCE challenge
#                       |
#                       v
#                    Google
#                       |
#               Alice authenticates
#                       |
#                       v
#              Authorization Code
#                       |
#                       v
#                    Smolink
#                       |
#             Check state
#             Check expiry
#             Check consumed
#                       |
#                       v
#              Send code + PKCE verifier
#                       |
#                       v
#                    Google
#                       |
#               Verify PKCE
#                       |
#                       v
#               Access/ID tokens
#                       |
#                       v
#                    Smolink
#                       |
#               Verify ID token
#               Check nonce
#                       |
#                       v
#                 Login Alice

# ===============================================================================
# 12. WHAT EACH ONE PROTECTS
# ===============================================================================

# STATE
#     Attack:
#         CSRF / Login CSRF

#     Question:
#         "Did I start this OAuth login?"

#     Check:
#         Returned state == stored state

# ------------------------------------------------------------

# NONCE
#     Attack:
#         Replay / injection of an ID token from another authentication flow

#     Question:
#         "Does this ID token belong to this login?"

#     Check:
#         ID-token nonce == stored nonce

# ------------------------------------------------------------

# PKCE
#     Attack:
#         Authorization code interception

#     Question:
#         "Does the client exchanging this code possess the original
#          secret verifier?"

#     Check:
#         SHA256(verifier) == original challenge

# ------------------------------------------------------------

# EXPIRY
#     Attack:
#         Long-lived abandoned/stolen OAuth authorization requests

#     Check:
#         Current time < expires_at

# ------------------------------------------------------------

# CONSUMED_AT
#     Attack:
#         Reuse of the same OAuth authorization request

#     Check:
#         consumed_at IS NULL

# ===============================================================================
# EASY MEMORY
# ===============================================================================

# STATE
#     → "Did I start this?"

# NONCE
#     → "Is this ID token for MY login?"

# PKCE
#     → "Do you have the secret needed to exchange this code?"

# EXPIRY
#     → "Is this login attempt still fresh?"

# CONSUMED
#     → "Has this login attempt already been used?"

# ===============================================================================
