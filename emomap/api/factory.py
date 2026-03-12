from fastapi import FastAPI

from .exception_handlers import register_exception_handlers
from .views import register_routers


def create_base_app():
    app = FastAPI(
        title="Emomap API",
    )

    register_routers(app)
    register_exception_handlers(app)

    return app

