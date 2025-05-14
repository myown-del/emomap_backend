from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, extract

from emomap.controllers.base import BaseController
from emomap.dto.emotion import EmotionCreateDTO, EmotionResponseDTO, EmotionDetailDTO
from emomap.infrastructure.db.repositories.emotions import EmotionRepository
from emomap.infrastructure.db.models.emotions import EmotionDB


class EmotionController(BaseController):
    def __init__(self, emotion_repository: EmotionRepository):
        self.emotion_repository = emotion_repository
    
    async def create_emotion(self, user_id: int, emotion_data: EmotionCreateDTO) -> EmotionResponseDTO:
        """
        Create a new emotion record
        """
        # Validate rating range
        if not 1 <= emotion_data.rating <= 10:
            raise ValueError("Rating must be between 1 and 10")
        
        # Create the emotion
        emotion = await self.emotion_repository.create(
            user_id=user_id,
            latitude=emotion_data.latitude,
            longitude=emotion_data.longitude,
            rating=emotion_data.rating,
            comment=emotion_data.comment
        )
        
        # Convert to DTO
        return self._model_validate(EmotionResponseDTO, emotion)
    
    async def get_emotion(self, emotion_id: int) -> Optional[EmotionDetailDTO]:
        """
        Get emotion by ID with user details
        """
        emotion = await self.emotion_repository.get_by_id(emotion_id)
        if not emotion:
            return None
            
        return self._model_validate(EmotionDetailDTO, emotion)
    
    async def get_emotion_by_unique_id(self, unique_id: str) -> Optional[EmotionDetailDTO]:
        """
        Get emotion by unique ID with user details
        """
        emotion = await self.emotion_repository.get_by_unique_id(unique_id)
        if not emotion:
            return None
            
        return self._model_validate(EmotionDetailDTO, emotion)
    
    async def get_user_emotions(self, user_id: int) -> list[EmotionResponseDTO]:
        """
        Get all emotions for a specific user
        """
        emotions = await self.emotion_repository.get_all_by_user_id(user_id)
        return [self._model_validate(EmotionResponseDTO, emotion) for emotion in emotions]
    
    async def delete_emotion(self, emotion_id: int) -> bool:
        """
        Delete an emotion by ID
        """
        return await self.emotion_repository.delete(emotion_id)
        
    async def get_weekly_statistics(self) -> List[Dict[str, Any]]:
        """
        Get average emotion rating for each day of the last 7 days
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Get average ratings by day
        results = await self.emotion_repository.get_average_rating_by_period(
            extract('day', EmotionDB.created_at),
            start_date,
            end_date
        )
        
        # Format the results with day names
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        today = datetime.utcnow().weekday()
        
        # Reorder days to have the correct 7-day window
        ordered_days = days[today:] + days[:today]
        
        # Create a dictionary of day to statistics
        day_stats = {
            int(result[0]): {  # Convert Decimal to int
                'period_label': days[(int(result[0]) - 1) % 7],  # Convert day number to day name
                'average_rating': float(result[1]),
                'count': int(result[2])
            } 
            for result in results
        }
        
        # Create a complete list for all 7 days, with zeros for missing days
        statistics = []
        for i in range(7):
            day = (end_date - timedelta(days=i)).day
            if day in day_stats:
                statistics.append(day_stats[day])
            else:
                statistics.append({
                    'period_label': ordered_days[i],
                    'average_rating': 0.0,
                    'count': 0
                })
        
        # Reverse to get chronological order
        statistics.reverse()
        
        return statistics
    
    async def get_monthly_statistics(self) -> List[Dict[str, Any]]:
        """
        Get average emotion rating for each week of the last month
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get average ratings by week
        results = await self.emotion_repository.get_average_rating_by_period(
            extract('week', EmotionDB.created_at),
            start_date,
            end_date
        )
        
        # Format the results
        statistics = []
        for week_num, avg_rating, count in results:
            # Calculate the start date of this week
            week_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            while week_start.isocalendar()[1] != int(week_num):  # Convert Decimal to int
                week_start -= timedelta(days=1)
            
            week_label = f"Week {int(week_num)} ({week_start.strftime('%b %d')})"  # Convert Decimal to int
            statistics.append({
                'period_label': week_label,
                'average_rating': float(avg_rating),
                'count': int(count)  # Convert Decimal to int
            })
        
        return statistics
    
    async def get_yearly_statistics(self) -> List[Dict[str, Any]]:
        """
        Get average emotion rating for each month of the last year
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date.replace(year=end_date.year - 1)
        
        # Get average ratings by month
        results = await self.emotion_repository.get_average_rating_by_period(
            extract('month', EmotionDB.created_at),
            start_date,
            end_date
        )
        
        # Format the results with month names
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create a dictionary of month to statistics
        month_stats = {
            int(result[0]): {  # Convert Decimal to int
                'period_label': months[int(result[0]) - 1],  # Convert month number to name
                'average_rating': float(result[1]),
                'count': int(result[2])  # Convert Decimal to int
            } 
            for result in results
        }
        
        # Create a complete list for all 12 months, with zeros for missing months
        statistics = []
        current_month = end_date.month
        
        # Start from 12 months ago and move forward
        for i in range(12):
            month = (current_month - 12 + i) % 12 + 1  # Calculate month number
            if month in month_stats:
                statistics.append(month_stats[month])
            else:
                statistics.append({
                    'period_label': months[month - 1],
                    'average_rating': 0.0,
                    'count': 0
                })
        
        return statistics 