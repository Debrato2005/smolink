#The future get_session() dependency must yield a usable async SQLAlchemy session.
import asyncio #Python’s asynchronous runtime so a normal pytest test can run async code
from sqlalchemy import text #imports SQLAlchemy’s explicit SQL-text wrapperfro
from app.db import session
def test_session_dependency_runs_select_one()-> None:
    async def check_connection()-> None:
        async for database_session in session.get_session():
            result=await database_session.execute(text("select 1"))

            assert result.scalar_one()==1

    asyncio.run(check_connection())