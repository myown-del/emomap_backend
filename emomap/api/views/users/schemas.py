from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    registration_date: datetime
    name: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """Request model for updating a user's profile"""
    name: Optional[str] = None
