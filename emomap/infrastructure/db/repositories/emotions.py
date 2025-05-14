import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models.emotions import EmotionDB


class EmotionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def create(self, user_id: int, latitude: float, longitude: float, rating: int, comment: str = None) -> EmotionDB:
        """
        Create a new emotion record
        """
        emotion = EmotionDB(
            unique_id=str(uuid.uuid4()),
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            rating=rating,
            comment=comment
        )
        
        self.session.add(emotion)
        await self.session.flush()
        return emotion
    
    async def get_by_id(self, emotion_id: int) -> EmotionDB:
        """
        Get emotion by ID
        """
        result = await self.session.execute(
            select(EmotionDB).where(EmotionDB.id == emotion_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_unique_id(self, unique_id: str) -> EmotionDB:
        """
        Get emotion by unique ID
        """
        result = await self.session.execute(
            select(EmotionDB).where(EmotionDB.unique_id == unique_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_user_id(self, user_id: int) -> list[EmotionDB]:
        """
        Get all emotions for a specific user
        """
        result = await self.session.execute(
            select(EmotionDB).where(EmotionDB.user_id == user_id)
        )
        return result.scalars().all()
    
    async def delete(self, emotion_id: int) -> bool:
        """
        Delete an emotion by ID
        """
        emotion = await self.get_by_id(emotion_id)
        if emotion:
            await self.session.delete(emotion)
            return True
        return False
        
    async def get_emotions_in_date_range(self, start_date: datetime, end_date: datetime) -> list[EmotionDB]:
        """
        Get all emotions created between start_date and end_date
        """
        result = await self.session.execute(
            select(EmotionDB)
            .where(EmotionDB.created_at >= start_date)
            .where(EmotionDB.created_at <= end_date)
            .order_by(EmotionDB.created_at)
        )
        return result.scalars().all()
        
    async def get_average_rating_by_period(self, 
                                          period_extract,
                                          start_date: datetime, 
                                          end_date: datetime) -> list[tuple]:
        """
        Get average rating of emotions grouped by a period
        
        Args:
            period_extract: SQLAlchemy extract function for the period (day, week, month, etc.)
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of tuples (period, average_rating, count)
        """
        result = await self.session.execute(
            select(
                period_extract,
                func.avg(EmotionDB.rating).label("average_rating"),
                func.count(EmotionDB.id).label("count")
            )
            .where(EmotionDB.created_at >= start_date)
            .where(EmotionDB.created_at <= end_date)
            .group_by(period_extract)
            .order_by(period_extract)
        )
        return result.all() 