import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload

from ..models.users import SessionDB, PasswordResetTokenDB
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
            joinedload(SessionDB.user)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_session(self, session_id: str) -> Optional[SessionDB]:
        """Get active session by ID (not expired)"""
        stmt = select(SessionDB).where(
            SessionDB.session_id == session_id,
            SessionDB.expires_at > datetime.utcnow()
        ).options(
            joinedload(SessionDB.user)
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

    async def create_password_reset_token(
        self,
        user_id: int,
        code: str,
        expires_at: datetime,
    ) -> PasswordResetTokenDB:
        token = PasswordResetTokenDB(
            user_id=user_id,
            code=code,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_used=False,
            attempts=0,
        )
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token

    async def get_latest_active_password_reset_token(
        self,
        user_id: int,
    ) -> Optional[PasswordResetTokenDB]:
        stmt = (
            select(PasswordResetTokenDB)
            .where(
                PasswordResetTokenDB.user_id == user_id,
                PasswordResetTokenDB.is_used.is_(False),
                PasswordResetTokenDB.expires_at > datetime.utcnow(),
            )
            .order_by(PasswordResetTokenDB.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_password_reset_token_by_id(
        self,
        token_id: int,
        user_id: int,
    ) -> Optional[PasswordResetTokenDB]:
        stmt = select(PasswordResetTokenDB).where(
            PasswordResetTokenDB.id == token_id,
            PasswordResetTokenDB.user_id == user_id,
            PasswordResetTokenDB.is_used.is_(False),
            PasswordResetTokenDB.expires_at > datetime.utcnow(),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_active_password_reset_token_by_code(
        self,
        code: str,
    ) -> Optional[PasswordResetTokenDB]:
        stmt = (
            select(PasswordResetTokenDB)
            .where(
                PasswordResetTokenDB.code == code,
                PasswordResetTokenDB.is_used.is_(False),
                PasswordResetTokenDB.expires_at > datetime.utcnow(),
            )
            .order_by(PasswordResetTokenDB.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_password_reset_attempts(self, token_id: int) -> None:
        stmt = (
            update(PasswordResetTokenDB)
            .where(PasswordResetTokenDB.id == token_id)
            .values(attempts=PasswordResetTokenDB.attempts + 1)
        )
        await self.session.execute(stmt)

    async def mark_password_reset_token_used(self, token_id: int) -> None:
        stmt = (
            update(PasswordResetTokenDB)
            .where(PasswordResetTokenDB.id == token_id)
            .values(is_used=True)
        )
        await self.session.execute(stmt)

    async def mark_all_password_reset_tokens_used(self, user_id: int) -> None:
        stmt = (
            update(PasswordResetTokenDB)
            .where(
                PasswordResetTokenDB.user_id == user_id,
                PasswordResetTokenDB.is_used.is_(False),
            )
            .values(is_used=True)
        )
        await self.session.execute(stmt)

    async def update_password_reset_token_expiry(
        self,
        token_id: int,
        expires_at: datetime,
    ) -> None:
        stmt = (
            update(PasswordResetTokenDB)
            .where(PasswordResetTokenDB.id == token_id)
            .values(expires_at=expires_at)
        )
        await self.session.execute(stmt)
