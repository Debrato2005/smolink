from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.rate_limit import limit_auth_write
from app.core.config import get_settings
from app.db.session import get_session

from app.services.email_service import (
    EmailDeliveryError,
    send_verification_email,
    send_password_reset_email,
)

from app.schemas.auth import (
    LoginRequest,
    PublicUserResponse,
    RegisterRequest,
    TokenPairResponse,
    RefreshRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.services.auth_service import (
    AccountLockedError,
    EmailTakenError,
    EmailUnverifiedError,
    InvalidCredentialsError,
    authenticate_user,
    issue_token_pair,
    register_user,
    InvalidRefreshTokenError,
    rotate_refresh_token,
    InvalidOrExpiredTokenError,
    verify_email,
    logout_refresh_token,
    request_password_reset,
    reset_password,
)
from app.utils.snowflake import SnowflakeGenerator

from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User

router=APIRouter(prefix="/auth", tags=["auth"])
generator = SnowflakeGenerator(
    worker_id=get_settings().snowflake_worker_id,
)
#@router.post("/register") registers the function underneath
#  it as the handler for a POST request to /register
@router.post( "/register",
    response_model=PublicUserResponse,
    status_code=status.HTTP_201_CREATED,)
async def register(
    payload:RegisterRequest,
    session:AsyncSession=Depends(get_session),
     _: None = Depends(limit_auth_write)
)->PublicUserResponse|JSONResponse:
    try:
        registration=await register_user(
            session=session,
            email=str(payload.email),
            password=payload.password,
            generator=generator,
        )
        user=registration.user
        
        await session.commit()
        await session.refresh(user)

        await send_verification_email(
            recipient_email=user.email,
            verification_token=registration.verification_token,
            idempotency_key=f"verification:{user.id}",
        )
        
    except EmailTakenError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "email_taken",
                "message": "Email is already registered",
            },
        )
    except IntegrityError:
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "email_taken",
                "message": "Email is already registered",
            },
        )

    return PublicUserResponse.model_validate(user)

# Duplicate-email handling has two layers:
# - EmailTakenError handles the normal case where the service detects an
#   existing normalized email before attempting an insert.
# - IntegrityError handles rare concurrent race conditions where two requests
#   pass the duplicate check simultaneously, and PostgreSQL's UNIQUE
#   constraint rejects the second insert. Both return the same 409 response.

@router.post("/login",
             response_model=TokenPairResponse,)
async def login(
    payload:LoginRequest,
    session:AsyncSession=Depends(get_session),
    _:None=Depends(limit_auth_write)
)->TokenPairResponse | JSONResponse:
    try:
        user=await authenticate_user(
            session=session,
            email=str(payload.email),
            password=payload.password,
        )
        token_pair=await issue_token_pair(
            session=session,
            user=user,
            generator=generator,
        )
        await session.commit()
    except InvalidCredentialsError:
        await session.commit() #to update the failed counter
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "invalid_credentials",
                "message": "Invalid email or password",
            },
        )
    except EmailUnverifiedError:
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "email_unverified",
                "message": "Email verification is required before login",
            },
        )
    except AccountLockedError:
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_423_LOCKED,
            content={
                "error": "account_locked",
                "message": "Account is temporarily locked",
            },
        )
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )

@router.post("/refresh",
    response_model=TokenPairResponse
)
async def refresh(
    payload:RefreshRequest,
    session: AsyncSession = Depends(get_session),
    _: None = Depends(limit_auth_write),
) -> TokenPairResponse | JSONResponse:
    try:
        token_pair=await rotate_refresh_token(
            session=session,
            refresh_token=payload.refresh_token,
            generator=generator
        )
        await session.commit()
    except InvalidRefreshTokenError:
        # A replay may revoke a token family, so preserve transaction changes.
        await session.commit()
        #Do not replace await session.commit() with rollback in the exception branch: 
        # a replayed refresh token intentionally revokes the token family and must persist 
        # that revocation.
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "invalid_refresh_token",
                "message": "Invalid refresh token",
            },
        )
    return TokenPairResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        expires_in=token_pair.expires_in,
    )
# Normally exceptions trigger a rollback, but refresh-token replay is different:
# replay detection revokes the entire refresh-token family before raising
# InvalidRefreshTokenError. Committing here preserves that security update. If
# no database changes were made (e.g. malformed or expired token), commit is a
# harmless no-op.

@router.post("/verify-email", response_model=PublicUserResponse)
async def verify_email_endpoint(
    payload:VerifyEmailRequest,
    session:AsyncSession=Depends(get_session),
    _:None=Depends(limit_auth_write),
)->PublicUserResponse | JSONResponse:
    try:
        user= await verify_email(
            session=session,
            token=payload.token,
        )
        await session.commit()
        await session.refresh(user)
    except InvalidOrExpiredTokenError:
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "invalid_or_expired_token",
                "message": "Invalid or expired token",
            },
        )

    return PublicUserResponse.model_validate(user)
# Convert the internal SQLAlchemy User model into the public response schema,
# exposing only the fields defined by PublicUserResponse before returning JSON.
# Map the internal database model to the public response model to avoid
# exposing internal-only fields (e.g. password_hash, auth_version).

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT,response_model=None)
async def logout(
    payload:RefreshRequest,
    session: AsyncSession=Depends(get_session),
    _:None=Depends(limit_auth_write),
    )->Response|JSONResponse:
    try:
        await logout_refresh_token(
            session=session,
            refresh_token=payload.refresh_token,
        )
        await session.commit()
    except InvalidRefreshTokenError:
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "invalid_refresh_token",
                "message": "Invalid refresh token",
            },
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=PublicUserResponse)
async def me(
    user:User=Depends(get_current_user),
)->PublicUserResponse:
    return PublicUserResponse.model_validate(user)

@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=None,
)
async def forgot_password(
    payload:ForgotPasswordRequest,
    session:AsyncSession=Depends(get_session),
    _:None=Depends(limit_auth_write)
)-> Response:

    result=await request_password_reset(
        session=session,
        email=str(payload.email),
        generator=generator,
    )
    await session.commit()

    if result is not None:
        try:
            await send_password_reset_email(
                recipient_email=result.user.email,
# `result` contains the User object, not a separate email field, so the
# user's email is accessed through `result.user.email`.
                reset_token=result.reset_token,
                idempotency_key=f"password-reset:{result.token_id}",
            )
        except EmailDeliveryError:
            pass
                
    return Response(status_code=status.HTTP_202_ACCEPTED)

@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None
)    
async def reset_password_endpoint(
    payload : ResetPasswordRequest,
    session : AsyncSession=Depends(get_session),
    _: None=Depends(limit_auth_write)
)->Response:
    try:
        await reset_password(
            session=session,
            token=payload.token,
            new_password=payload.new_password,
        )
        await session.commit()

    except InvalidOrExpiredTokenError:
        await session.rollback()
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error":"invalid_or_expired_token",
                "message":"Invalid or expired token",
            },
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)