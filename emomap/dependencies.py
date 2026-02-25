from typing import AsyncGenerator, Type, TypeVar, Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .app_state import AppState
from .controllers.base import BaseController
from .controllers.users import UserController
from .controllers.auth import AuthController
from .controllers.emotions import EmotionController
from .config import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_TIMEOUT_SECONDS,
    SMTP_USERNAME,
    SMTP_USE_STARTTLS,
    SMTP_USE_TLS,
)
from .infrastructure.db.repositories.base import BaseRepository
from .infrastructure.db.repositories.users import UserRepository
from .infrastructure.db.repositories.auth import AuthRepository
from .infrastructure.db.repositories.emotions import EmotionRepository
from .services.email_sender import SMTPEmailSender

RepoType = TypeVar("RepoType", bound=BaseRepository)
CtrlType = TypeVar("CtrlType", bound=BaseController)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    app_state: AppState = request.app.state.app_state
    async with app_state.session_factory() as session:
        async with session.begin():
            yield session


def create_repo_dependency(repo_type: Type[RepoType]):
    def _get_repo(session: AsyncSession = Depends(get_db_session)) -> RepoType:
        return repo_type(session=session)
    return _get_repo


def create_controller_dependency(controller_type: Type[CtrlType]) -> Callable[..., CtrlType]:
    if controller_type == AuthController:
        def _get_auth_controller(
            auth_repo: AuthRepository = Depends(AuthRepositoryDep),
            user_repo: UserRepository = Depends(UserRepositoryDep)
        ) -> AuthController:
            email_sender = SMTPEmailSender(
                host=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USERNAME,
                password=SMTP_PASSWORD,
                from_email=SMTP_FROM_EMAIL,
                use_tls=SMTP_USE_TLS,
                use_starttls=SMTP_USE_STARTTLS,
                timeout=SMTP_TIMEOUT_SECONDS,
            )
            return AuthController(
                auth_repo=auth_repo,
                user_repo=user_repo,
                email_sender=email_sender,
            )
        return _get_auth_controller
    elif controller_type == UserController:
        def _get_user_controller(
            user_repo: UserRepository = Depends(UserRepositoryDep)
        ) -> UserController:
            return UserController(user_repo=user_repo)
        return _get_user_controller
    elif controller_type == EmotionController:
        def _get_emotion_controller(
            emotion_repo: EmotionRepository = Depends(EmotionRepositoryDep)
        ) -> EmotionController:
            return EmotionController(emotion_repository=emotion_repo)
        return _get_emotion_controller
    else:
        raise ValueError(f"Unsupported controller type: {controller_type}")


# Repositories
UserRepositoryDep = create_repo_dependency(UserRepository)
AuthRepositoryDep = create_repo_dependency(AuthRepository)
EmotionRepositoryDep = create_repo_dependency(EmotionRepository)

# Controllers
UserControllerDep = create_controller_dependency(UserController)
AuthControllerDep = create_controller_dependency(AuthController)
EmotionControllerDep = create_controller_dependency(EmotionController)
