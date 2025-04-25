from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                        async_sessionmaker,
                                        create_async_engine)

from .config import DB_URL


class AppState:
    def __init__(self):
        self.engine: AsyncEngine = create_async_engine(DB_URL, echo=False)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def close(self):
        await self.engine.dispose()

    
