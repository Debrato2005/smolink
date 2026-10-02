# Pydantic validates request data and filters public response fields.
# Literal["bearer"] permits only that token_type value.
# Plain classes require explicit construction and validation.
# Dataclasses generate constructors and comparison methods without type validation.
# SQLAlchemy models define database tables. Pydantic models define API contracts.

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from typing import Literal

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

class LoginRequest(BaseModel):
    email:EmailStr
    password: str = Field(min_length=12, max_length=128)

class RefreshRequest(BaseModel):
    refresh_token:str=Field(min_length=1)

class TokenPairResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:Literal["bearer"]="bearer"
    expires_in : int =Field(gt=0)

class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=1)
    

class ForgotPasswordRequest(BaseModel):
    email:EmailStr

class ResetPasswordRequest(BaseModel):
    token:str
    new_password:str=Field(min_length=12, max_length=128)

class ResendVerificationRequest(BaseModel):
    email: EmailStr
