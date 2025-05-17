import uuid
from typing import Optional

from ..dto.user import UserDTO
from ..infrastructure.db.repositories.auth import AuthRepository
from ..infrastructure.db.repositories.users import UserRepository
from ..utils.password import hash_password, verify_password
from .base import BaseController


class AuthController(BaseController):
    def __init__(self, auth_repo: AuthRepository, user_repo: UserRepository):
        self.auth_repo = auth_repo
        self.user_repo = user_repo
    
    async def register(self, email: str, password: str) -> str:
        """Register a new user and create a session"""
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash the password securely
        password_hash = hash_password(password)
        
        # Create user
        user = await self.user_repo.create_user(
            email=email,
            password_hash=password_hash,
            name=None
        )
        
        # Create session for the new user
        session = await self.auth_repo.create_session(user.id)
        
        return session.session_id
    
    async def login(self, email: str, password: str) -> str:
        """Login user with email and password"""
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify the password using secure verification
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        # Create a new session
        session = await self.auth_repo.create_session(user.id)
        
        return session.session_id
    
    async def logout(self, session_id: str) -> bool:
        """Logout user by deleting session"""
        return await self.auth_repo.delete_session(session_id)
    
    async def validate_session(self, session_id: str) -> Optional[UserDTO]:
        """Validate session and return user if valid"""
        session = await self.auth_repo.get_active_session(session_id)
        if not session:
            return None
        
        user = await self.user_repo.get_user_by_id(session.user_id)
        if not user:
            return None
        
        return self._model_validate(UserDTO, user) 