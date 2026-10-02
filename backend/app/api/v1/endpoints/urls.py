# APIRouter groups URL handlers under the versioned route prefix.
# FastAPI resolves Depends(get_session) once for the request dependency chain.
# The session is shared with services and repositories within that request.
# Do not share AsyncSession across concurrent requests.
# Repositories flush SQL. This route commits the completed creation workflow.
# Without commit, session closure rolls back the insert.
# A previous missing commit prevented duplicate-alias tests from seeing a row.
# Business errors map first. PostgreSQL SQLSTATE 23505 handles uniqueness races.
# The unused dependency result `_` still enforces the creation rate limit.

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.url import CreateUrlRequest, CreateUrlResponse
from app.services.url_service import AliasTakenError, InvalidExpiryError, create_short_url
from app.utils.aliases import InvalidAliasError
from app.utils.snowflake import SnowflakeGenerator

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.rate_limit import limit_url_creation

from app.api.v1.dependencies.auth import get_optional_current_user
from app.models.user import User

router=APIRouter(prefix="/urls",tags=["urls"])
generator=SnowflakeGenerator(worker_id=get_settings().snowflake_worker_id,)

@router.post(
    "",
    response_model=CreateUrlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_url(  
    payload: CreateUrlRequest,
    session: AsyncSession=Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
    _: None = Depends(limit_url_creation),
     )->CreateUrlResponse|JSONResponse:
    try:
        url=await create_short_url(
            session=session,
            destination=str(payload.destination),
            alias=payload.alias,
            expires_at=payload.expires_at,
            owner_id=current_user.id if current_user is not None else None,
            generator=generator,
        )
        await session.commit()
        await session.refresh(url)

    except InvalidExpiryError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "invalid_expiry",
                "message": str(error),
            },
        )
    except InvalidAliasError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "invalid_alias",
                "message": str(error),
            },
        )
    except AliasTakenError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=
                {
                    "error":"alias_taken",
                    "message":"Alias is already taken",
                },
            )
    
    except IntegrityError as error:
        await session.rollback()

        if getattr(error.orig, "sqlstate", None) == "23505":
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "alias_taken",
                    "message": "Alias is already taken",
                },
            )

        raise
   
    
    public_base_url=get_settings().public_base_url.rstrip("/")
    return CreateUrlResponse (
        id=url.id,
        short_code=url.short_code,
        short_url=f"{public_base_url}/{url.short_code}",
        destination=url.destination,
        expires_at=url.expires_at,
        created_at=url.created_at,
    )
