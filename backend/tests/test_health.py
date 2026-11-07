
from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import health


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_health_connected(monkeypatch):
    """
    Test successful database health check.
    """

    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: True,
    )

    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["database"] == "connected"


def test_database_health_disconnected(monkeypatch):
    """
    Test database health check when PostgreSQL is unavailable.
    """

    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: False,
    )

    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection unavailable"
