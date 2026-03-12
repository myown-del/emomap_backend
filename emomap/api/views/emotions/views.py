from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import StreamingResponse
from typing import Annotated, List, Optional
from enum import Enum
import io
import csv
from datetime import datetime, date

from emomap.controllers.emotions import EmotionController
from emomap.dto.emotion import EmotionCreateDTO
from emomap.infrastructure.db.models.users import UserDB
from emomap.api.views.auth.dependencies import get_current_user
from emomap.dependencies import EmotionControllerDep
from .schemas import EmotionCreate, EmotionResponse, EmotionStatisticsResponse, StatisticPeriod

router = APIRouter(prefix="/emotions", tags=["Emotions"])


@router.post("/", response_model=EmotionResponse, status_code=status.HTTP_201_CREATED)
async def create_emotion(
    emotion_data: EmotionCreate,
    current_user: Annotated[UserDB, Depends(get_current_user)],
    emotion_controller: EmotionController = Depends(EmotionControllerDep),
):
    dto_data = EmotionCreateDTO(
        latitude=emotion_data.latitude,
        longitude=emotion_data.longitude,
        rating=emotion_data.rating,
        comment=emotion_data.comment
    )
    
    if not 1 <= dto_data.rating <= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 10"
        )
    
    return await emotion_controller.create_emotion(
        user_id=current_user.id,
        emotion_data=dto_data
    )


@router.get("/me", response_model=List[EmotionResponse])
async def get_user_emotions(
    current_user: Annotated[UserDB, Depends(get_current_user)],
    emotion_controller: EmotionController = Depends(EmotionControllerDep),
    min_rating: Optional[int] = Query(None, ge=1, le=10, description="Filter emotions with rating greater than or equal to this value"),
    max_rating: Optional[int] = Query(None, ge=1, le=10, description="Filter emotions with rating less than or equal to this value"),
    date_from: Optional[date] = Query(None, description="Filter emotions created after this date (inclusive)"),
    date_to: Optional[date] = Query(None, description="Filter emotions created before this date (inclusive)")
):
    emotions = await emotion_controller.get_user_emotions(user_id=current_user.id)
    
    filtered_emotions = emotions
    
    if min_rating is not None:
        filtered_emotions = [emotion for emotion in filtered_emotions if emotion.rating >= min_rating]
        
    if max_rating is not None:
        filtered_emotions = [emotion for emotion in filtered_emotions if emotion.rating <= max_rating]
    
    if date_from is not None:
        # Convert date to datetime with time at start of day (00:00:00)
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        filtered_emotions = [emotion for emotion in filtered_emotions if emotion.created_at >= date_from_dt]
    
    if date_to is not None:
        # Convert date to datetime with time at end of day (23:59:59)
        date_to_dt = datetime.combine(date_to, datetime.max.time())
        filtered_emotions = [emotion for emotion in filtered_emotions if emotion.created_at <= date_to_dt]
        
    return filtered_emotions


class StatisticsPeriod(str, Enum):
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


@router.get("/statistics/average/{period_type}", response_model=EmotionStatisticsResponse)
async def get_emotion_statistics(
    period_type: StatisticsPeriod = Path(..., description="The time period to get statistics for: week, month, or year"),
    emotion_controller: EmotionController = Depends(EmotionControllerDep)
):
    """
    Get average rating of emotions for different time periods:
    
    - week: Average rating for each day of the last 7 days
    - month: Average rating for each week of the last month
    - year: Average rating for each month of the last year
    """
    if period_type == StatisticsPeriod.WEEK:
        stats = await emotion_controller.get_weekly_statistics()
    elif period_type == StatisticsPeriod.MONTH:
        stats = await emotion_controller.get_monthly_statistics()
    elif period_type == StatisticsPeriod.YEAR:
        stats = await emotion_controller.get_yearly_statistics()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period type: {period_type}"
        )
    
    # Convert to response model
    periods = [
        StatisticPeriod(
            period_label=period['period_label'],
            average_rating=period['average_rating'],
            count=period['count']
        )
        for period in stats
    ]
    
    return EmotionStatisticsResponse(
        period_type=period_type,
        periods=periods
    )


@router.get("/csv-export", response_class=StreamingResponse)
async def export_user_emotions_csv(
    current_user: Annotated[UserDB, Depends(get_current_user)],
    emotion_controller: EmotionController = Depends(EmotionControllerDep),
):
    """
    Export all emotions for the current user as a CSV file
    """
    # Get emotions for the current user
    emotions = await emotion_controller.get_user_emotions(user_id=current_user.id)
    
    # Create in-memory string buffer
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    
    # Write CSV header
    writer.writerow([
        "ID", "Latitude", "Longitude",
        "Rating", "Comment", "Created At"
    ])
    
    # Write emotion data
    for emotion in emotions:
        writer.writerow([
            emotion.id,
            emotion.latitude,
            emotion.longitude,
            emotion.rating,
            emotion.comment or "",  # Handle None values
            emotion.created_at.isoformat()
        ])
    
    # Reset buffer position to the beginning
    buffer.seek(0)
    
    # Generate filename based on current date
    filename = f"emotions_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    
    # Return streaming response with CSV data
    return StreamingResponse(
        buffer, 
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    ) 
