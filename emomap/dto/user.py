from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserProfileDTO(BaseModel):
    id: int
    unique_id: str
    name: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class UserDTO(BaseModel):
    id: int
    unique_id: str
    email: EmailStr
    registration_date: datetime
    profile: Optional[UserProfileDTO] = None

    class Config:
        from_attributes = True
        populate_by_name = True