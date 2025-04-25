from fastapi import FastAPI

from .views import register_routers


async def create_base_app():
    app = FastAPI(
        title="Emomap API",
    )
    
    register_routers(app)
    
    return app

