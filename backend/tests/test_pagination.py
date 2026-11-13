
from fastapi.testclient import TestClient

from app.main import app
from app.db.queries import customers, ledger
from app.api.routes import ledger as ledger_routes


ORG_ID = "11111111-1111-4111-8111-111111111111"
CUSTOMER_ID = "22222222-2222-4222-8222-222222222222"


def test_customer_pagination(monkeypatch):

    expected = {
        "items": [],
        "total": 45,
        "limit": 10,
        "offset": 20,
    }

    monkeypatch.setattr(
        customers,
        "get_customers",
        lambda **kwargs: expected,
    )

    with TestClient(app) as client:
        response = client.get(
            "/customers/?limit=10&offset=20",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 200
    assert response.json()["total"] == 45
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 20


def test_customer_pagination_limit_cannot_exceed_100():

    with TestClient(app) as client:
        response = client.get(
            "/customers/?limit=101",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 422


def test_customer_pagination_rejects_negative_offset():

    with TestClient(app) as client:
        response = client.get(
            "/customers/?offset=-1",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 422


def test_ledger_pagination(monkeypatch):

    # The route does `from app.services.ledger import get_customer_ledger`,
    # so patch the name where the route looks it up, not the service module.
    monkeypatch.setattr(
        ledger_routes,
        "get_customer_ledger",
        lambda **kwargs: {
            "items": [],
            "total": 30,
            "limit": 5,
            "offset": 10,
        },
    )

    with TestClient(app) as client:
        response = client.get(
            f"/ledger/customers/{CUSTOMER_ID}/entries?limit=5&offset=10",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 200
    assert response.json()["total"] == 30
    assert response.json()["limit"] == 5
    assert response.json()["offset"] == 10
