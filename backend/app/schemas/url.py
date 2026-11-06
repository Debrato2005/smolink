# Request schemas validate API input. Response schemas define public output.
# Schema validation does not replace business rules or database constraints.
# alias defaults to None. The service selects a generated code when absent.
# from_attributes=True reads ORM attributes instead of dictionary keys.

from datetime import datetime
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl, field_validator

# Matches the String(2048) destination column, so an oversized URL is a 422 instead of a database error.
MAX_DESTINATION_LENGTH = 2048

class CreateUrlRequest(BaseModel):
    destination:HttpUrl
    alias:str |None=Field(default=None, max_length=64)
    # A naive datetime cannot be compared with the UTC clock, so it is rejected here.
    expires_at: AwareDatetime|None=None

    @field_validator("destination")
    @classmethod
    def _destination_fits_column(cls, value: HttpUrl) -> HttpUrl:
        if len(str(value)) > MAX_DESTINATION_LENGTH:
            raise ValueError(f"destination must be at most {MAX_DESTINATION_LENGTH} characters")
        return value

class CreateUrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    short_code: str
    short_url: str
    destination: HttpUrl
    expires_at: datetime | None
    created_at: datetime
