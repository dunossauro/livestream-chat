from pytest import fixture
from fastapi.testclient import TestClient

from app.app import app


@fixture
def client():
    app.router.on_startup = []

    with TestClient(app) as client:
        yield client
