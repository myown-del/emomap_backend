from fastapi import APIRouter, FastAPI

from .users import router as users_router


def register_routers(app: FastAPI):
    main_router = APIRouter(prefix="/api")
    main_router.include_router(users_router)

    app.include_router(main_router)
