from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.auth import UserResponse

class UserFilter(BaseModel):
    search: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int

class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_verified: Optional[bool] = None