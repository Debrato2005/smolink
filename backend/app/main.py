from fastapi import FastAPI  # see fastapi docs
# from pydantic import BaseModel # pydantic for schema validation

def create_app()->FastAPI:
    app=FastAPI(
        title="smolink",
        version="0.1.0",
    )
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