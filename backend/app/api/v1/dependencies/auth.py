from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.repositories.user_repository import get_user_by_id
from app.utils.security import InvalidAccessTokenError, decode_access_token

#Because OAuth2PasswordBearer is a class specifically designed by FastAPI 
# to encapsulate all the OAuth2/Bearer-token behavior.

# OAuth2PasswordBearer is a FastAPI class that already contains the logic for
# extracting a Bearer token from the current request's Authorization header.
# We create an instance and configure its token endpoint; Depends() then tells
# FastAPI to call this instance for each request and inject the extracted token.
oauth2_scheme=OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)#actually reads the Authorization header to read the bearer token

# Depends() is used when FastAPI should resolve something for the current
# request, such as request-specific data, request-scoped resources, or reusable
# dependency chains. OAuth2PasswordBearer extracts the current request's Bearer
# token, get_session creates and cleans up a request-scoped DB session, and
# limit_auth_write checks the current request's rate limit. The Snowflake
# generator is already-created application-level state, so it is passed
# explicitly instead of being injected.

async def get_current_user(
    token:str=Depends(oauth2_scheme),
    session:AsyncSession=Depends(get_session),
    )->User:
    settings=get_settings()

    try:
        claims=decode_access_token(
            token,
            secret=settings.jwt_secret,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )

        user_id=int(str(claims["sub"]))
        auth_version=int(claims["auth_version"])

    except (InvalidAccessTokenError,KeyError,TypeError,ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from error

    user= await get_user_by_id(session,user_id)
    if(
        user is None
        or user.email_verified_at is None
        or user.auth_version!=auth_version):
# auth_version is a server-side token invalidation/version number for the user.
# The JWT stores the auth_version that was current when it was issued, while
# the database stores the user's current auth_version. If they differ, the JWT
# is considered invalid and is rejected.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return user




# ===============================================================================
# WHY DO WE NEED get_current_user() IF SERVICES ALREADY HANDLE AUTHENTICATION?
# ===============================================================================

# Services handle the APPLICATION/BUSINESS LOGIC.

# For example:

#     register_user()
#         → create a user

#     login_user()
#         → verify credentials and create tokens

#     refresh_token()
#         → validate/rotate refresh tokens

# But an endpoint still needs to answer:

#     "WHO is making this request?"

# That is the job of get_current_user().

# ===============================================================================
# AUTHENTICATION DEPENDENCY
# ===============================================================================

#     Authorization: Bearer <access_token>
#                     ↓
#               get_current_user()
#                     ↓
#               extract token
#                     ↓
#               validate JWT
#                     ↓
#               get user ID from `sub`
#                     ↓
#               query database
#                     ↓
#               check:
#                   - user exists
#                   - email is verified
#                   - auth_version matches
#                     ↓
#                 return User
#                     ↓
#               endpoint receives:
#                   user: User


# ===============================================================================
# WHY NOT PUT THIS INSIDE EVERY SERVICE?
# ===============================================================================

# If every protected endpoint/service performed:

#     decode JWT
#     get user ID
#     query user
#     check auth_version
#     check verification

# then the same authentication code would be repeated everywhere.

# Instead:

#     FastAPI dependency
#             ↓
#        get_current_user()
#             ↓
#        authenticated User
#             ↓
#        service/business logic


# The service can then focus on WHAT the application should do, while the
# dependency handles WHO the requester is.


# ===============================================================================
# EXAMPLE
# ===============================================================================

# Instead of:

#     @router.get("/me")
#     async def me(token=...):
#         # decode JWT
#         # find user
#         # validate user
#         # business logic
#         ...

# we use:

#     @router.get("/me")
#     async def me(
#         user: User = Depends(get_current_user),
#     ):
#         return PublicUserResponse.model_validate(user)


# FastAPI runs get_current_user() BEFORE the endpoint.

# If authentication fails:

#     get_current_user()
#         ↓
#     HTTP 401
#         ↓
#     endpoint never runs


# If authentication succeeds:

#     get_current_user()
#         ↓
#     User object
#         ↓
#     /me endpoint
#         ↓
#     response


# ===============================================================================
# SERVICE VS DEPENDENCY
# ===============================================================================

# DEPENDENCY:

#     "Who are you?"

#     → extract access token
#     → validate JWT
#     → identify user
#     → verify current authentication state


# SERVICE:

#     "What should we do?"

#     → register user
#     → perform business operation
#     → update data
#     → create/modify application resources


# So they are complementary, not duplicates.

# ===============================================================================
# MEMORY
# ===============================================================================

#     Dependency
#         → AUTHENTICATION / request context
#         → "Who is the current user?"

#     Service
#         → BUSINESS LOGIC
#         → "What should we do for this user?"
