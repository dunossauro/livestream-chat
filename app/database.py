from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)

async_session = async_sessionmaker(engine)


async def get_session():
    async with async_session() as session:
        yield session
