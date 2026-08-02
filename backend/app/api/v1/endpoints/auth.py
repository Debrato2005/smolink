from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.rate_limit import limit_auth_write
from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.auth import PublicUserResponse, RegisterRequest
from app.services.auth_service import EmailTakenError, register_user
from app.utils.snowflake import SnowflakeGenerator

router=APIRouter(prefix="/auth", tags=["auth"])
generator = SnowflakeGenerator(
    worker_id=get_settings().snowflake_worker_id,
)
@router.post(
    "/register",
    response_model=PublicUserResponse,
    status_code=status.HTTP_201_CREATED,)
async def register(
    payload:RegisterRequest,
    session:AsyncSession=Depends(get_session),
     _: None = Depends(limit_auth_write)
)->PublicUserResponse|JSONResponse:
    try:
        user=await register_user(
            session=session,
            email=str(payload.email),
            password=payload.password,
            generator=generator,
        )
        await session.commit()
        await session.refresh(user)
        
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
