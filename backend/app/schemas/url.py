# Pydantic schemas for the URL API.
# These schemas define the structure of data exchanged between the client
# and the backend. They validate incoming request data and ensure outgoing
# responses follow a consistent format.
# Request schemas (e.g., CreateUrlRequest):
#     Client  --->  Backend
# Response schemas (e.g., CreateUrlResponse):
#     Backend --->  Client
# Schemas only describe and validate data. They do not contain business
# logic, database operations, or API route handling.
from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl

class CreateUrlRequest(BaseModel):
    destination:HttpUrl
    alias:str |None=None #str or None if nothing default is none
    expires_at: datetime|None=None

class CreateUrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Enables conversion from SQLAlchemy ORM objects to this Pydantic schema
# by reading object attributes (obj.field) instead of dictionary keys.
    id: int
    short_code: str
    short_url: str
    destination: HttpUrl
    expires_at: datetime | None
    created_at: datetime