import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.app import app
from app.database import get_session
from app.models import table_registry, YTChatToken


@pytest_asyncio.fixture(scope='session')
async def session():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)

        async with AsyncSession(engine) as session:
            yield session

        async with engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.router.on_startup = []
        app.dependency_overrides[get_session] = get_session_override
        yield client


@pytest_asyncio.fixture()
async def token(session):
    token = YTChatToken('mock_id', 'mock_token')
    session.add(token)
    await session.commit()

    return token
