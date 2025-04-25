from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.users import UserDB
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def get_user_by_id(self, user_id: int) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, hashed_password: str) -> UserDB:
        db_user = UserDB(email=email, hashed_password=hashed_password)
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserDB]:
        stmt = select(UserDB).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()