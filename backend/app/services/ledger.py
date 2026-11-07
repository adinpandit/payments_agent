from app.db.queries import ledger
from app.db.queries import customers

def get_customer_balance(organization_id, customer_id):
    customer = customers.get_customer(
        organization_id=organization_id,
        customer_id=customer_id,
    )

    if customer is None:
        return None

    return ledger.get_customer_balance(
        organization_id=organization_id,
        customer_id=customer_id,
    )

def get_customer_ledger(organization_id, customer_id,):
    customer = customers.get_customer(
        organization_id=organization_id,
        customer_id=customer_id,
    )