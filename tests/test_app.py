from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from app.app import app



def test_health_should_return_ok(client: TestClient):
    response = client.get('/health')
    assert response.json() == {'status': 'OK'}


def test_root_should_return_template(client: TestClient):
    response = client.get('/')
    assert 'doctype html' in response.content.decode()
    assert response.status_code == 200

def test_get_highlight_should_return_template(client: TestClient):
    response = client.get('/highlight')
    assert 'doctype html' in response.content.decode()
    assert response.status_code == 200


def test_post_highlight_should_call_ws_broadcast(client: TestClient):
    mock = AsyncMock()

    data = {'name': 'test', 'message': 'test'}
    expected = data | {'channel': 'event', 'type': 'textMessageEvent'}

    with app.container.ws_manager.override(mock):
        response = client.post('/highlight', json=data)

        assert response.status_code == 201
        assert mock.broadcast.called
        mock.broadcast.assert_called_with(expected)


def test_highlight_should_raise_error_when_ws_disconnect(
        client: TestClient, caplog
):
    mock = AsyncMock()
    mock.broadcast.side_effect = Exception('Error!')

    data = {'name': 'test', 'message': 'test'}

    with app.container.ws_manager.override(mock):
        client.post('/highlight', json=data)

    assert caplog.record_tuples == [('app.routes', 50, 'Deu ex: Error!')]
