import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from app.app import app
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
def client():
    return TestClient(app)


@pytest_asyncio.fixture()
async def token(session):
    token = YTChatToken('mock_id', 'mock_token')
    session.add(token)
    await session.commit()

    return token
