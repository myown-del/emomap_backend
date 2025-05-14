from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from .user import UserDTO


class EmotionCreateDTO(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    rating: int = Field(..., ge=1, le=10, description="Emotion rating from 1 to 10")
    comment: Optional[str] = Field(None, max_length=256, description="Optional comment about the emotion")


class EmotionResponseDTO(BaseModel):
    id: int
    unique_id: str
    latitude: float
    longitude: float
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
        populate_by_name = True


class EmotionDetailDTO(EmotionResponseDTO):
    user: Optional[UserDTO] = None

    class Config:
        from_attributes = True
        populate_by_name = True 