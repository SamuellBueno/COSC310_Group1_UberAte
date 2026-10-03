def test_healthAPI_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}