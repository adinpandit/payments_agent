from fastapi.testclient import TestClient

from app.main import app
from app.db.queries import customers, organizations


ORG_ID = "11111111-1111-4111-8111-111111111111"
CUSTOMER_ID = "22222222-2222-4222-8222-222222222222"


def test_create_customer(monkeypatch):

    monkeypatch.setattr(
        organizations,
        "get_organization",
        lambda organization_id: {
            "id": organization_id,
            "name": "Aditya Traders",
        },
    )

    monkeypatch.setattr(
        customers,
        "create_customer",
        lambda **kwargs: {
            "id": CUSTOMER_ID,
            "organization_id": ORG_ID,
            "name": kwargs["name"],
            "phone": kwargs["phone"],
            "email": kwargs["email"],
            "address": kwargs["address"],
            "created_at": "2026-11-06T10:00:00Z",
        },
    )

    with TestClient(app) as client:
        response = client.post(
            "/customers/",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "name": "Rahul Enterprises",
                "phone": "9876543210",
                "email": "rahul@example.com",
                "address": "Pune",
            },
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Rahul Enterprises"
    assert response.json()["organization_id"] == ORG_ID