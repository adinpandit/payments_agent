from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import ledger as ledger_routes


ORG_ID = "11111111-1111-4111-8111-111111111111"
CUSTOMER_ID = "22222222-2222-4222-8222-222222222222"


def test_customer_not_found_for_another_organization(monkeypatch):

    monkeypatch.setattr(
        ledger_routes,
        "get_customer_ledger",
        lambda **kwargs: None,
    )

    with TestClient(app) as client:
        response = client.get(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 404


def test_customer_balance_can_be_negative_after_overpayment(monkeypatch):

    monkeypatch.setattr(
        ledger_routes,
        "get_customer_balance",
        lambda **kwargs: {
            "customer_id": CUSTOMER_ID,
            "total_debit": Decimal("5000.00"),
            "total_credit": Decimal("7000.00"),
            "outstanding_balance": Decimal("-2000.00"),
        },
    )

    with TestClient(app) as client:
        response = client.get(
            f"/ledger/customers/{CUSTOMER_ID}/balance",
            headers={"X-Organization-ID": ORG_ID},
        )

    assert response.status_code == 200
    assert response.json()["outstanding_balance"] == "-2000.00"


def test_payment_cannot_be_a_debit():

    with TestClient(app) as client:
        response = client.post(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "entry_type": "payment",
                "direction": "debit",
                "amount": "1000.00",
            },
        )

    assert response.status_code == 422


def test_zero_amount_is_rejected():

    with TestClient(app) as client:
        response = client.post(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "entry_type": "sale",
                "direction": "debit",
                "amount": "0",
            },
        )

    assert response.status_code == 422


def test_negative_amount_is_rejected():

    with TestClient(app) as client:
        response = client.post(
            f"/ledger/customers/{CUSTOMER_ID}/entries",
            headers={"X-Organization-ID": ORG_ID},
            json={
                "entry_type": "sale",
                "direction": "debit",
                "amount": "-500",
            },
        )

    assert response.status_code == 422