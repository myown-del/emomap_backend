from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserProfileResponse(BaseModel):
    id: int
    unique_id: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    unique_id: str
    email: EmailStr
    registration_date: datetime
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """Request model for updating a user's profile"""
    name: Optional[str] = None
