from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.users import UserDB, UserProfileDB
from .base import BaseRepository


class UserRepository(BaseRepository):
    async def get_user_by_id(self, user_id: int) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.id == user_id).options(
            joinedload(UserDB.profile),
            joinedload(UserDB.sessions)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserDB | None:
        stmt = select(UserDB).where(UserDB.email == email).options(
            joinedload(UserDB.profile),
            joinedload(UserDB.sessions)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_user(
        self, 
        unique_id: str,
        email: str, 
        password_hash: str
    ) -> UserDB:
        db_user = UserDB(
            unique_id=unique_id,
            email=email, 
            password_hash=password_hash
        )
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user
    
    async def create_user_profile(
        self,
        unique_id: str,
        user_id: int,
        name: Optional[str] = None
    ) -> UserProfileDB:
        db_profile = UserProfileDB(
            unique_id=unique_id,
            user_id=user_id,
            name=name
        )
        self.session.add(db_profile)
        await self.session.flush()
        await self.session.refresh(db_profile)
        return db_profile
    
    async def update_user_profile(
        self,
        profile_id: int,
        name: Optional[str] = None
    ) -> UserProfileDB:
        # Get the profile first
        stmt = select(UserProfileDB).where(UserProfileDB.id == profile_id)
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise ValueError(f"Profile with ID {profile_id} not found")
            
        # Update fields if provided
        if name is not None:
            profile.name = name
            
        await self.session.flush()
        return profile

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[UserDB]:
        stmt = select(UserDB).options(
            joinedload(UserDB.profile),
            joinedload(UserDB.sessions)
        ).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()