from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.db.queries import customers, ledger
from app.api.routes import ledger as ledger_routes


ORG_ID = "11111111-1111-4111-8111-111111111111"
CUSTOMER_ID = "22222222-2222-4222-8222-222222222222"


def test_create_payment(monkeypatch):

    monkeypatch.setattr(
        customers,
        "get_customer",
        lambda **kwargs: {
            "id": CUSTOMER_ID,
            "organization_id": ORG_ID,
        },
    )

    monkeypatch.setattr(
        ledger,
        "create_ledger_entry",
        lambda **kwargs: {
            "id": "33333333-3333-4333-8333-333333333333",
            "customer_id": CUSTOMER_ID,
            "entry_type": "payment",
            "direction": "credit",
            "amount": Decimal("3000.00"),
            "description": "Payment received",
            "created_at": "2026-11-06T10:00:00Z",
        },
    )

    with TestClient(app) as client:
        response = client.post(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "entry_type": "payment",
                "direction": "credit",
                "amount": "3000.00",
                "description": "Payment received",
            },
        )

    assert response.status_code == 201
    assert response.json()["direction"] == "credit"
    assert response.json()["amount"] == "3000.00"


def test_get_customer_balance(monkeypatch):

    monkeypatch.setattr(
        ledger_routes,
        "get_customer_balance",
        lambda **kwargs: {
            "customer_id": CUSTOMER_ID,
            "total_debit": Decimal("7000.00"),
            "total_credit": Decimal("3000.00"),
            "outstanding_balance": Decimal("4000.00"),
        },
    )

    with TestClient(app) as client:
        response = client.get(
            f"/ledger/customers/{CUSTOMER_ID}/balance",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 200
    assert response.json()["total_debit"] == "7000.00"
    assert response.json()["total_credit"] == "3000.00"
    assert response.json()["outstanding_balance"] == "4000.00"


def test_sale_cannot_be_a_credit():

    with TestClient(app) as client:
        response = client.post(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "entry_type": "sale",
                "direction": "credit",
                "amount": "1000.00",
            },
        )

    assert response.status_code == 422