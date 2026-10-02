# OAuth2PasswordBearer extracts a Bearer token from Authorization.
# Depends() asks FastAPI to resolve that request dependency.
# get_current_user() validates the JWT and loads the current User.
# Verification and auth_version checks use current PostgreSQL state.
# A mismatched auth_version rejects an old access token after password reset.
# The optional extractor returns None when it extracts no Bearer token.
# A supplied invalid Bearer token still returns 401.
# URL creation uses this result for ownership and the matching rate-limit scope.
# Services own business operations. This dependency identifies the requester.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.repositories.user_repository import get_user_by_id
from app.utils.security import InvalidAccessTokenError, decode_access_token


oauth2_scheme=OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return user

optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)
async def get_optional_current_user(
    token: str | None = Depends(optional_oauth2_scheme),
    session: AsyncSession = Depends(get_session),
)->User|None:
    if token is None:
        return None

    return await get_current_user(
        token=token,
        session=session,
    )
