
import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.api.routes import health


@pytest.fixture(autouse=True)
def disable_database_lifecycle(monkeypatch):
    """
    Prevent tests from opening or closing a real PostgreSQL
    connection pool during FastAPI startup and shutdown.
    """

    monkeypatch.setattr(
        main_module,
        "open_pool",
        lambda: None,
    )

    monkeypatch.setattr(
        main_module,
        "close_pool",
        lambda: None,
    )


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
    monkeypatch.setattr(
        health,
        "check_database_connection",
        lambda: False,
    )

    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection unavailable"
