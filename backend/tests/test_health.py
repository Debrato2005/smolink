from fastapi.testclient import TestClient #Imports FastAPI’s testing tool. It can call your API without starting a real server.

from app.main import app #Imports the same FastAPI application object from app/main.py

def test_health_returns_ok() -> None:
    client = TestClient(app)

    response=client.get("/health")

    assert response.status_code == 200
    assert response.json() == { "status" : "ok"}