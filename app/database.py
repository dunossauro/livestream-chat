from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)

async_session = async_sessionmaker(engine)


async def get_session() -> (
    AsyncGenerator[
        AsyncSession,
        None,
    ]
):  # pagma: no cover
    async with async_session() as session:
        yield session
