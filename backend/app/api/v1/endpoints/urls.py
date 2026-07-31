from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.url import CreateUrlRequest, CreateUrlResponse
from app.services.url_service import AliasTakenError, InvalidExpiryError, create_short_url
from app.utils.aliases import InvalidAliasError
from app.utils.snowflake import SnowflakeGenerator

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.dependencies.rate_limit import limit_guest_creation

router=APIRouter(prefix="/urls",tags=["urls"])#A router (APIRouter) in FastAPI is a tool used to organize code, group endpoints, and split large projects into multiple files
generator=SnowflakeGenerator(worker_id=get_settings().snowflake_worker_id,)

@router.post(
    "",
    response_model=CreateUrlResponse,
    status_code=status.HTTP_201_CREATED, #If function succeeds instead of default 200
)
async def create_url(  payload: CreateUrlRequest,
                     session: AsyncSession=Depends(get_session), #session should be an AsyncSession object with default value after =
                     _: None = Depends(limit_guest_creation), #by convention, _ means: "I know this variable exists, but I intentionally won't use it."
                     )->CreateUrlResponse|JSONResponse:
    try:
        url=await create_short_url(
            session=session,
            destination=str(payload.destination),
            alias=payload.alias,
            expires_at=payload.expires_at,
            owner_id=None,
            generator=generator,
        )
        await session.commit() #important look down at comment as well as in test_url_creation
    except AliasTakenError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=
            {
                "error":"alias_taken",
                "message":"Alias is already taken",
            },
        )
    except InvalidExpiryError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "invalid_expiry",
                "message": str(error),
            },
        )
    # except InvalidExpiryError as error:
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         detail=str(error),
    #     )       from error
    except InvalidAliasError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": "invalid_alias",
                "message": str(error),
            },
        )
   
    
    public_base_url=get_settings().public_base_url.rstrip("/")
    return CreateUrlResponse (
        id=url.id,
        short_code=url.short_code,
        short_url=f"{public_base_url}/{url.short_code}",
        destination=url.destination,
        expires_at=url.expires_at,
        created_at=url.created_at,
    )

# Why use Depends(get_session) instead of a global session?
#
# SnowflakeGenerator is a long-lived, reusable object.
# It only generates IDs, doesn't hold external resources,
# and is safe to share across all requests.
#
# AsyncSession is different:
# - Represents a database connection/transaction.
# - Must be unique for each request.
# - Needs to be opened before use and closed afterwards.
# - Sharing one session across multiple requests can mix
#   transactions, cause race conditions, and corrupt state.
#
# Depends(get_session) tells FastAPI:
#   "Before calling this endpoint, create a new AsyncSession,
#    inject it into the 'session' parameter, and clean it up
#    automatically after the request finishes."
#
# Internally, FastAPI does something similar to:
#
# session = await get_session()
# await create_url(payload=payload, session=session)
#
# The session is then passed to the service and repository so
# they all use the same transaction for that request.


# Commit at the API (transaction) boundary.
#
# Repository:
#   - Performs database operations (add, update, delete, queries).
#   - May call flush() to send SQL and obtain generated values.
#   - MUST NOT commit, so repositories remain reusable and composable.
#
# Service:
#   - Contains business logic.
#   - Coordinates one or more repository calls.
#   - Also should not commit.
#
# Endpoint:
#   - Owns the transaction.
#   - Commits only after the entire operation succeeds.
#   - If an exception occurs before commit, the transaction is rolled back.
#
# Earlier bug:
# Repository only called session.flush(). Without commit, the request ended,
# the session closed, and SQLAlchemy rolled back the transaction. The first
# URL was never persisted, so duplicate-alias tests incorrectly succeeded.
    
