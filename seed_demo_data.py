#!/usr/bin/env python3
import asyncio
import os
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Final

from dotenv import load_dotenv
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from emomap.infrastructure.db.models.emotions import EmotionDB
from emomap.infrastructure.db.models.users import (
    PasswordResetTokenDB,
    SessionDB,
    UserDB,
)
from emomap.utils.password import hash_password

REQUIRED_DB_ENV_VARS: Final[tuple[str, ...]] = (
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
)

DEMO_USER_COUNT: Final[int] = 1
EMOTIONS_PER_USER: Final[int] = 365
DEMO_PASSWORD: Final[str] = "demo12345"
DEMO_EMAIL_PREFIX: Final[str] = "demo_user_"
DEMO_EMAIL_DOMAIN: Final[str] = "emomap.demo"

MOSCOW_LAT_MIN: Final[float] = 55.491307
MOSCOW_LAT_MAX: Final[float] = 55.957565
MOSCOW_LON_MIN: Final[float] = 37.319328
MOSCOW_LON_MAX: Final[float] = 37.967427

DEMO_COMMENTS: Final[tuple[str | None, ...]] = (
    "Good productive day",
    "A little tired but calm",
    "Feeling optimistic",
    "Traffic was stressful",
    "Great walk in the city",
    "Focused and motivated",
    "Need better sleep",
    "Everything feels balanced",
    None,
)


@dataclass
class SeedSummary:
    users_created: int
    emotions_created: int
    date_from: date
    date_to: date
    credentials: list[tuple[str, str]]


def build_db_url_from_env() -> str:
    env_values = {name: (os.getenv(name) or "").strip() for name in REQUIRED_DB_ENV_VARS}
    missing = [name for name, value in env_values.items() if not value]
    if missing:
        missing_str = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variables: {missing_str}")

    host = "localhost" if env_values["DB_HOST"] in ["postgres", "db"] else env_values["DB_HOST"]

    return (
        "postgresql+asyncpg://"
        f"{env_values['DB_USER']}:{env_values['DB_PASSWORD']}"
        f"@{host}:{env_values['DB_PORT']}/{env_values['DB_NAME']}"
    )


async def delete_existing_demo_data(session) -> None:
    demo_user_ids_result = await session.execute(
        select(UserDB.id).where(
            UserDB.email.like(f"{DEMO_EMAIL_PREFIX}%"),
            UserDB.email.like(f"%@{DEMO_EMAIL_DOMAIN}"),
        )
    )
    demo_user_ids = [user_id for user_id in demo_user_ids_result.scalars().all()]
    if not demo_user_ids:
        return

    await session.execute(delete(EmotionDB).where(EmotionDB.user_id.in_(demo_user_ids)))
    await session.execute(delete(SessionDB).where(SessionDB.user_id.in_(demo_user_ids)))
    await session.execute(
        delete(PasswordResetTokenDB).where(
            PasswordResetTokenDB.user_id.in_(demo_user_ids)
        )
    )
    await session.execute(delete(UserDB).where(UserDB.id.in_(demo_user_ids)))


def random_moscow_coordinates() -> tuple[float, float]:
    latitude = random.uniform(MOSCOW_LAT_MIN, MOSCOW_LAT_MAX)
    longitude = random.uniform(MOSCOW_LON_MIN, MOSCOW_LON_MAX)
    return latitude, longitude


async def seed_demo_data(session) -> SeedSummary:
    await delete_existing_demo_data(session)

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=EMOTIONS_PER_USER - 1)

    credentials: list[tuple[str, str]] = []
    emotions_created = 0

    for user_index in range(1, DEMO_USER_COUNT + 1):
        email = f"{DEMO_EMAIL_PREFIX}{user_index}@{DEMO_EMAIL_DOMAIN}"
        db_user = UserDB(
            email=email,
            password_hash=hash_password(DEMO_PASSWORD),
            name=f"Demo User {user_index}",
        )
        session.add(db_user)
        await session.flush()

        credentials.append((email, DEMO_PASSWORD))

        emotions: list[EmotionDB] = []
        for day_offset in range(EMOTIONS_PER_USER):
            entry_date = start_date + timedelta(days=day_offset)
            created_at = datetime.combine(entry_date, time(hour=12, minute=0))
            latitude, longitude = random_moscow_coordinates()
            emotions.append(
                EmotionDB(
                    user_id=db_user.id,
                    latitude=latitude,
                    longitude=longitude,
                    rating=random.randint(1, 10),
                    comment=random.choice(DEMO_COMMENTS),
                    created_at=created_at,
                )
            )

        session.add_all(emotions)
        emotions_created += len(emotions)

    return SeedSummary(
        users_created=DEMO_USER_COUNT,
        emotions_created=emotions_created,
        date_from=start_date,
        date_to=today,
        credentials=credentials,
    )


def print_credentials_table(credentials: list[tuple[str, str]]) -> None:
    email_width = max([len("email")] + [len(email) for email, _ in credentials])
    password_width = max([len("password")] + [len(password) for _, password in credentials])

    header = f"{'email'.ljust(email_width)} | {'password'.ljust(password_width)}"
    separator = f"{'-' * email_width}-+-{'-' * password_width}"
    print(header)
    print(separator)

    for email, password in credentials:
        print(f"{email.ljust(email_width)} | {password.ljust(password_width)}")


def print_seed_summary(summary: SeedSummary) -> None:
    print("Demo data seeded successfully.")
    print(f"Users created: {summary.users_created}")
    print(f"Emotions created: {summary.emotions_created}")
    print(
        "Date range: "
        f"{summary.date_from.isoformat()} to {summary.date_to.isoformat()}"
    )
    print()
    print("Login credentials:")
    print_credentials_table(summary.credentials)


async def run() -> int:
    load_dotenv()

    try:
        db_url = build_db_url_from_env()
        print(db_url)
    except RuntimeError as exc:
        print(f"Failed to load database configuration: {exc}", file=sys.stderr)
        return 1

    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    summary: SeedSummary | None = None
    try:
        async with session_factory() as session:
            try:
                summary = await seed_demo_data(session)
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    except Exception as exc:
        print(f"Failed to seed demo data: {exc}", file=sys.stderr)
        return 1
    finally:
        await engine.dispose()

    print_seed_summary(summary)
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
