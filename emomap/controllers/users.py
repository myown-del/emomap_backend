from typing import Sequence

from ..dto.user import UserDTO
from ..infrastructure.db.models.users import UserDB
from ..infrastructure.db.repositories.users import UserRepository
from .base import BaseController


class UserController(BaseController):
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_all(self, limit: int = 100, skip: int = 0) -> Sequence[UserDTO]:
        db_users = await self.user_repo.get_all_users(limit=limit, skip=skip)
        return [UserDTO.model_validate(user) for user in db_users]

    async def get_by_id(self, user_id: int) -> UserDTO | None:
        db_user = await self.user_repo.get_user_by_id(user_id)
        return UserDTO.model_validate(db_user) if db_user else None

    async def get_by_email(self, email: str) -> UserDTO | None:
        db_user = await self.user_repo.get_user_by_email(email)
        return UserDTO.model_validate(db_user) if db_user else None

    async def create(self, email: str, password: str) -> UserDTO:
        if not password:
            raise ValueError("Password cannot be empty")
        hashed_password = password + "_hashed"

        async with self.user_repo.session.begin():
            new_db_user = await self.user_repo.create_user(
                email=email,
                hashed_password=hashed_password
            )
        return UserDTO.model_validate(new_db_user)