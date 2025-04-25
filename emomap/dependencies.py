from typing import AsyncGenerator, Type, TypeVar, Callable

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from .app_state import AppState
from .controllers.base import BaseController
from .controllers.users import UserController
from .infrastructure.db.repositories.base import BaseRepository
from .infrastructure.db.repositories.users import UserRepository

RepoType = TypeVar("RepoType", bound=BaseRepository)
CtrlType = TypeVar("CtrlType", bound=BaseController)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    app_state: AppState = request.app.state.app_state
    async with app_state.session_factory() as session:
        yield session


def create_repo_dependency(repo_type: Type[RepoType]):
    def _get_repo(session: AsyncSession = Depends(get_db_session)) -> RepoType:
        return repo_type(session=session)
    return _get_repo


def create_controller_dependency(controller_type: Type[CtrlType]) -> Callable[..., CtrlType]:
    def _get_controller(
        user_repo: UserRepository = Depends(UserRepositoryDep)
    ) -> CtrlType:
        return controller_type(user_repo=user_repo)

    return _get_controller

# Репозитории
UserRepositoryDep = create_repo_dependency(UserRepository)

# Контроллеры
UserControllerDep = create_controller_dependency(UserController)