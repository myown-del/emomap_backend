import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from ..api.factory import create_base_app
from ..app_state import AppState

lifespan_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state = AppState()
    lifespan_state["app_state"] = app_state
    app.state.app_state = app_state
    yield
    await app_state.close()
    lifespan_state.clear()


def create_app() -> FastAPI:
    app = create_base_app()
    app.router.lifespan_context = lifespan
    return app
