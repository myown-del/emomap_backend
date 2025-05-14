import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.users import UserDB, SessionDB, UserProfileDB
from .base import BaseRepository


class AuthRepository(BaseRepository):
    async def create_session(self, user_id: int) -> SessionDB:
        """Create a new session for the user"""
        session = SessionDB(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        self.session.add(session)
        await self.session.flush()
        await self.session.refresh(session)
        return session
    
    async def get_session(self, session_id: str) -> Optional[SessionDB]:
        """Get session by ID"""
        stmt = select(SessionDB).where(SessionDB.session_id == session_id).options(
            joinedload(SessionDB.user).joinedload(UserDB.profile)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_session(self, session_id: str) -> Optional[SessionDB]:
        """Get active session by ID (not expired)"""
        stmt = select(SessionDB).where(
            SessionDB.session_id == session_id,
            SessionDB.expires_at > datetime.utcnow()
        ).options(
            joinedload(SessionDB.user).joinedload(UserDB.profile)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID"""
        stmt = delete(SessionDB).where(SessionDB.session_id == session_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
    
    async def delete_all_user_sessions(self, user_id: int) -> int:
        """Delete all sessions for a user"""
        stmt = delete(SessionDB).where(SessionDB.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount 