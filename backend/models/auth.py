from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class UserInDB(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    hashed_password: str
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

class OTPRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None