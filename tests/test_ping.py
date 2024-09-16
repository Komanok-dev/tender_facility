from fastapi.testclient import TestClient

from backend.main import app

BASE_URL = "http://localhost:8080/api"


client = TestClient(app)


def test_ping():
    response = client.get(f"{BASE_URL}/ping")
    print(type(response.text))
    assert response.status_code == 200
    assert response.text == '"OK"'
