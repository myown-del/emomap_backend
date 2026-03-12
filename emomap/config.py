import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class AppEnvironment(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


def _parse_environment() -> AppEnvironment:
    raw_environment = os.getenv("ENVIRONMENT")
    if raw_environment is None:
        raw_environment = os.getenv("environment")

    if raw_environment is None or not raw_environment.strip():
        raise ValueError(
            "ENVIRONMENT is required and must be one of: dev, test, prod"
        )

    normalized_environment = raw_environment.strip().lower()
    try:
        return AppEnvironment(normalized_environment)
    except ValueError as exc:
        raise ValueError(
            f"Invalid ENVIRONMENT '{raw_environment}'. Allowed values: dev, test, prod"
        ) from exc


ENVIRONMENT = _parse_environment()

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
API_RELOAD = _to_bool(os.getenv("API_RELOAD"), True)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_USE_TLS = _to_bool(os.getenv("SMTP_USE_TLS"), False)
SMTP_USE_STARTTLS = _to_bool(os.getenv("SMTP_USE_STARTTLS"), True)
SMTP_TIMEOUT_SECONDS = int(os.getenv("SMTP_TIMEOUT_SECONDS", "10"))

PASSWORD_RESET_CODE_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_CODE_TTL_MINUTES", "10"))
PASSWORD_RESET_MAX_ATTEMPTS = int(os.getenv("PASSWORD_RESET_MAX_ATTEMPTS", "5"))
PASSWORD_RESET_TOKEN_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_TTL_MINUTES", "15"))
PASSWORD_RESET_SECRET = os.getenv("PASSWORD_RESET_SECRET", "change-me-password-reset-secret")
