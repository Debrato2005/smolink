from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class RegisterRequest(BaseModel):
    email:EmailStr 
    password: str=Field(min_length=12,max_length=128)

class PublicUserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int
    email:EmailStr
    email_verified_at:datetime|None
    created_at:datetime
    updated_at:datetime


#without pydantic no validation it will be just type hints
# also BaseModel parses an Parsing also includes type conversion.
#The automatic creation of payload from the request body is what BaseModel enables in FastAPI. Without it, a plain class does not receive that automatic treatment.
#
# Choosing between data containers:
#
# Plain class (__init__):
# - Full control, but you write the constructor and all validation yourself.
#
# @dataclass:
# - Automatically generates __init__, __repr__, __eq__, etc.
# - Stores data only; type hints are NOT validated at runtime.
#
# Pydantic BaseModel:
# - Automatically generates the constructor.
# - Validates and converts input using type annotations.
# - Parses JSON, serializes responses, and integrates directly with FastAPI.
# - Best suited for external/untrusted data such as HTTP requests, responses,
#   configuration, and API payloads.
#
# In this project:
# - SQLAlchemy models -> Database tables.
# - @dataclass -> Simple internal value objects (e.g. RateLimitResult).
# - BaseModel -> API request/response schemas with automatic validation.


