import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.app import app
from app.database import get_session
from app.models import Base


@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        poolclass=StaticPool,
        connect_args={'check_same_thread': False},
    )
    Base.metadata.create_all(engine)

    _session = sessionmaker(bind=engine)

    yield _session()

    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.router.on_startup = []
        app.dependency_overrides[get_session] = get_session_override
        yield client
