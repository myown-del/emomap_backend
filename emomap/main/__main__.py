import uvicorn

from config import API_PORT, API_RELOAD

uvicorn.run(
    "app:create_app",
    factory=True,
    host="0.0.0.0",
    port=API_PORT,
    reload=API_RELOAD,
)
