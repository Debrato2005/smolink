from fastapi import FastAPI  # See FastAPI documentation.
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



# Register fixed routes before any future /{short_code} route.
# A path operation is an HTTP route.
# @app.get("/") #path_operation decorator
# async def root(): #path_operation function
#     return {"message": "Hello, Debrato"}
