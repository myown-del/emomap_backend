from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserDTO(BaseModel):
    id: int
    email: EmailStr
    registration_date: datetime
    name: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True