from fastapi import APIRouter, FastAPI

from .users.views import router as users_router
from .auth.views import router as auth_router
from .emotions import router as emotions_router


def register_routers(app: FastAPI):
    api_router = APIRouter(prefix="/api")
    api_router.include_router(users_router)
    api_router.include_router(auth_router)
    api_router.include_router(emotions_router)

    app.include_router(api_router)
