# The session dependency must yield a usable async SQLAlchemy session.
# asyncio.run() bridges this synchronous test to its async database check.
# sqlalchemy.text() wraps the explicit SELECT 1 statement.

import asyncio
from sqlalchemy import text
from app.db import session
def test_session_dependency_runs_select_one()-> None:
    async def check_connection()-> None:
        async for database_session in session.get_session():
            result=await database_session.execute(text("select 1"))

            assert result.scalar_one()==1

    asyncio.run(check_connection())
