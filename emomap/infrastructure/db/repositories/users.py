from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.users import UserDB
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def get_user_by_id(self, user_id: int) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.id == user_id).options(
            joinedload(UserDB.sessions)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.email == email).options(
            joinedload(UserDB.sessions)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_user(
        self, 
        email: str, 
        password_hash: str,
        name: Optional[str] = None
    ) -> UserDB:
        db_user = UserDB(
            email=email, 
            password_hash=password_hash,
            name=name
        )
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user
    
    async def update_user(
        self,
        user_id: int,
        name: Optional[str] = None
    ) -> UserDB:
        # Get the user first
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
            
        # Update fields if provided
        if name is not None:
            user.name = name
            
        await self.session.flush()
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserDB]:
        stmt = select(UserDB).options(
            joinedload(UserDB.sessions)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def update_password_hash(self, user_id: int, password_hash: str) -> UserDB:
        stmt = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        user.password_hash = password_hash
        await self.session.flush()
        return user
