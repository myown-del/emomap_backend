import uuid
from typing import Sequence, Optional

from ..dto.user import UserDTO
from ..infrastructure.db.repositories.users import UserRepository
from ..utils.password import hash_password
from .base import BaseController

EMAIL_CONFLICT_MESSAGE = "User with this email already exists"


class UserController(BaseController):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_all(self, limit: int = 100, skip: int = 0) -> Sequence[UserDTO]:
        db_users = await self.user_repo.get_all_users(limit=limit, skip=skip)
        return [self._model_validate(UserDTO, user) for user in db_users]

    async def get_by_id(self, user_id: int) -> UserDTO | None:
        db_user = await self.user_repo.get_user_by_id(user_id)
        return self._model_validate(UserDTO, db_user) if db_user else None

    async def get_by_email(self, email: str) -> UserDTO | None:
        db_user = await self.user_repo.get_user_by_email(email)
        return self._model_validate(UserDTO, db_user) if db_user else None
    
    async def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> UserDTO:
        """
        Update a user
        """
        # Check if user exists
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        if email is not None:
            existing_user = await self.user_repo.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValueError(EMAIL_CONFLICT_MESSAGE)

        password_hash = hash_password(password) if password is not None else None
            
        # Update user
        updated_user = await self.user_repo.update_user(
            user_id=user_id,
            name=name,
            email=email,
            password_hash=password_hash,
        )
            
        return self._model_validate(UserDTO, updated_user)
