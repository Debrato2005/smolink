# Request schemas validate API input. Response schemas define public output.
# Schema validation does not replace business rules or database constraints.
# alias defaults to None. The service selects a generated code when absent.
# from_attributes=True reads ORM attributes instead of dictionary keys.

from datetime import datetime
from pydantic import BaseModel, ConfigDict, HttpUrl

class CreateUrlRequest(BaseModel):
    destination:HttpUrl
    alias:str |None=None
    expires_at: datetime|None=None

class CreateUrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    short_code: str
    short_url: str
    destination: HttpUrl
    expires_at: datetime | None
    created_at: datetime
