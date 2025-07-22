# app/schemas.py

from pydantic import BaseModel, EmailStr
from enum import Enum

# Enum to enforce valid user types
class UserType(str, Enum):
    client = "client"
    ops = "ops"

# Schema for creating a new user (sign up)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: UserType

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for returning user data in responses (excluding password)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    user_type: UserType

    class Config:
        orm_mode = True  # Allows returning SQLAlchemy models directly
