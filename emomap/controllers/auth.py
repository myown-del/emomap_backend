import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from ..config import (
    ENVIRONMENT,
    AppEnvironment,
    PASSWORD_RESET_CODE_TTL_MINUTES,
    PASSWORD_RESET_MAX_ATTEMPTS,
)
from ..dto.user import UserDTO
from ..infrastructure.db.repositories.auth import AuthRepository
from ..infrastructure.db.repositories.users import UserRepository
from ..services.email_sender import EmailSender
from ..utils.password import hash_password, verify_password
from .base import BaseController

from aiosmtplib.errors import SMTPException


logger = logging.getLogger("uvicorn.error")


class AuthController(BaseController):
    def __init__(
        self,
        auth_repo: AuthRepository,
        user_repo: UserRepository,
        email_sender: EmailSender,
    ):
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.email_sender = email_sender
    
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

    async def request_password_reset(self, email: str) -> None:
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return

        code = f"{secrets.randbelow(10000):04d}"
        expires_at = datetime.utcnow() + timedelta(minutes=PASSWORD_RESET_CODE_TTL_MINUTES)

        await self.auth_repo.mark_all_password_reset_tokens_used(user.id)
        await self.auth_repo.create_password_reset_token(
            user_id=user.id,
            code=code,
            expires_at=expires_at,
        )

        if ENVIRONMENT == AppEnvironment.DEV:
            logger.info(
                "Password reset code generated (dev mode): email=%s code=%s",
                user.email,
                code,
            )
            return

        try:
            await self.email_sender.send_password_reset_code(
                to_email=user.email,
                code=code,
            )
        except SMTPException as exc:
            raise RuntimeError("Failed to send reset code") from exc

    async def verify_password_reset_code(self, email: str, code: str) -> bool:
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return False

        reset_record = await self.auth_repo.get_latest_active_password_reset_token(user.id)
        if not reset_record:
            return False

        await self.auth_repo.increment_password_reset_attempts(reset_record.id)
        current_attempts = reset_record.attempts + 1

        if current_attempts > PASSWORD_RESET_MAX_ATTEMPTS:
            return False

        return reset_record.code == code

    async def confirm_password_reset(self, reset_token: str, new_password: str) -> None:
        reset_record = await self.auth_repo.get_latest_active_password_reset_token_by_code(
            reset_token
        )
        if not reset_record:
            raise ValueError("Invalid or expired reset token")

        if reset_record.attempts == 0:
            raise ValueError("Reset token is not verified")

        if reset_record.attempts > PASSWORD_RESET_MAX_ATTEMPTS:
            raise ValueError("Too many verification attempts")

        user_id = reset_record.user_id
        new_password_hash = hash_password(new_password)
        await self.user_repo.update_password_hash(user_id=user_id, password_hash=new_password_hash)
        await self.auth_repo.mark_all_password_reset_tokens_used(user_id=user_id)
        await self.auth_repo.delete_all_user_sessions(user_id=user_id)
