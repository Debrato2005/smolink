from fastapi import FastAPI  # see fastapi docs
from pydantic import BaseModel # pydantic for schema validation

app = FastAPI()

#order of path operatons does matter
#path_operation=route 
@app.get("/") #path_operation decorator
async def root(): #path_operation function
    return {"message": "Hello, Debrato"} 