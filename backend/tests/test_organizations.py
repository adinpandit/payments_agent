from fastapi.testclient import TestClient

from app.main import app
from app.db.queries import organizations


def test_create_organization(monkeypatch):

    expected = {
        "id": "11111111-1111-4111-8111-111111111111",
        "name": "Aditya Traders",
        "created_at": "2026-11-06T10:00:00Z",
    }

    monkeypatch.setattr(
        organizations,
        "create_organization",
        lambda name: expected,
    )

    with TestClient(app) as client:
        response = client.post(
            "/organizations/",
            json={"name": "Aditya Traders"},
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Aditya Traders"