from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class EmotionCreate(BaseModel):
    """Request model for creating a new emotion"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    rating: int = Field(..., ge=1, le=10, description="Emotion rating from 1 to 10")
    comment: Optional[str] = Field(None, max_length=256, description="Optional comment about the emotion")


class EmotionResponse(BaseModel):
    """Response model for emotion data"""
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


class StatisticPeriod(BaseModel):
    """A single period's statistics"""
    period_label: str = Field(..., description="Label for the time period (e.g., day, week, month)")
    average_rating: float = Field(..., description="Average rating during this period")
    count: int = Field(..., description="Number of emotions in this period")


class EmotionStatisticsResponse(BaseModel):
    """Response model for emotion statistics"""
    period_type: str = Field(..., description="Type of period (week, month, or year)")
    periods: List[StatisticPeriod] = Field(..., description="Statistics for each period")