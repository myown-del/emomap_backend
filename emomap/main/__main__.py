import uvicorn

from emomap.config import API_PORT, API_RELOAD

uvicorn.run(
    "emomap.main.app:create_app",
    factory=True,
    host="0.0.0.0",
    port=API_PORT,
    reload=API_RELOAD,
)
