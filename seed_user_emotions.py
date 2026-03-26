#!/usr/bin/env python3
import argparse
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
from emomap.infrastructure.db.models.users import UserDB

REQUIRED_DB_ENV_VARS: Final[tuple[str, ...]] = (
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_NAME",
)

DEFAULT_EMOTIONS_PER_USER: Final[int] = 365

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
    user_id: int
    email: str
    emotions_created: int
    emotions_deleted: int
    date_from: date
    date_to: date


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed emotion records for an existing user by email."
    )
    parser.add_argument("email", help="Existing user email")
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_EMOTIONS_PER_USER,
        help=f"Number of days to seed (default: {DEFAULT_EMOTIONS_PER_USER})",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Keep existing emotions and append new ones instead of replacing them",
    )
    return parser.parse_args()


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


def random_moscow_coordinates() -> tuple[float, float]:
    latitude = random.uniform(MOSCOW_LAT_MIN, MOSCOW_LAT_MAX)
    longitude = random.uniform(MOSCOW_LON_MIN, MOSCOW_LON_MAX)
    return latitude, longitude


async def seed_user_emotions(
    session,
    email: str,
    days: int,
    append: bool,
) -> SeedSummary:
    if days <= 0:
        raise ValueError("--days must be greater than 0")

    user = await session.scalar(select(UserDB).where(UserDB.email == email))
    if user is None:
        raise ValueError(f"User with email {email!r} not found")

    emotions_deleted = 0
    if not append:
        delete_result = await session.execute(
            delete(EmotionDB).where(EmotionDB.user_id == user.id)
        )
        emotions_deleted = delete_result.rowcount or 0

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=days - 1)

    emotions: list[EmotionDB] = []
    for day_offset in range(days):
        entry_date = start_date + timedelta(days=day_offset)
        created_at = datetime.combine(entry_date, time(hour=12, minute=0))
        latitude, longitude = random_moscow_coordinates()
        emotions.append(
            EmotionDB(
                user_id=user.id,
                latitude=latitude,
                longitude=longitude,
                rating=random.randint(1, 10),
                comment=random.choice(DEMO_COMMENTS),
                created_at=created_at,
            )
        )

    session.add_all(emotions)

    return SeedSummary(
        user_id=user.id,
        email=user.email,
        emotions_created=len(emotions),
        emotions_deleted=emotions_deleted,
        date_from=start_date,
        date_to=today,
    )


def print_seed_summary(summary: SeedSummary, append: bool) -> None:
    print("User emotion data seeded successfully.")
    print(f"User ID: {summary.user_id}")
    print(f"Email: {summary.email}")
    print(f"Emotions created: {summary.emotions_created}")
    if append:
        print("Emotions deleted: 0 (append mode)")
    else:
        print(f"Emotions deleted: {summary.emotions_deleted}")
    print(
        "Date range: "
        f"{summary.date_from.isoformat()} to {summary.date_to.isoformat()}"
    )


async def run() -> int:
    args = parse_args()
    load_dotenv()

    try:
        db_url = build_db_url_from_env()
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
                summary = await seed_user_emotions(
                    session=session,
                    email=args.email,
                    days=args.days,
                    append=args.append,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    except Exception as exc:
        print(f"Failed to seed user emotions: {exc}", file=sys.stderr)
        return 1
    finally:
        await engine.dispose()

    print_seed_summary(summary, append=args.append)
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(run()))


if __name__ == "__main__":
    main()
