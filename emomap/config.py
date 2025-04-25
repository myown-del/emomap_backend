import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DB_URL_FORMAT = "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_URL = DB_URL_FORMAT.format(
    DB_USER=DB_USER,
    DB_PASSWORD=DB_PASSWORD,
    DB_HOST=DB_HOST,
    DB_PORT=DB_PORT,
    DB_NAME=DB_NAME,
)

API_PORT = os.getenv("API_PORT", 8080)
API_RELOAD = os.getenv("API_RELOAD", True)
