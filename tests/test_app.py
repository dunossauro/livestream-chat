def test_health_should_return_ok(client):
    response = client.get('/health')
    assert response.json() == {'status': 'OK'}


def test_root_should_return_template(client):
    response = client.get('/')
    assert 'doctype html' in response.content.decode()
    assert response.status_code == 200
