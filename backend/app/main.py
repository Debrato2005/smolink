from fastapi import FastAPI  # see fastapi docs
# from pydantic import BaseModel # pydantic for schema validation
from app.api.v1.router import router as api_v1_router

def create_app()->FastAPI:
    app=FastAPI(
        title="smolink",
        version="0.1.0",
    )

    app.include_router(api_v1_router, prefix="/api/v1")
    
    @app.get("/health")
    async def health() -> dict[str,str]:
        return { "status": "ok" }
    return app
app=create_app()



#order of path operatons does matter
#path_operation=route 
# @app.get("/") #path_operation decorator
# async def root(): #path_operation function
#     return {"message": "Hello, Debrato"} 