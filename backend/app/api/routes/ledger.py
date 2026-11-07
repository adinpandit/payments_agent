from uuid import UUID
from fastapi import APIRouter, Header, HTTPException
from app.db.queries import customers, ledger
from app.schemas.ledger import (
    LedgerEntryCreate,
    LedgerEnryResponse,
    CustomerBalanceResponse,
)
from app.services.ledger import(
    get_customer_balance,
    get_customer_ledger,
)

router = APIRouter(
    prefix = "/ledger",
    tags = ["ledger"],
)

@router.post(
    "/customers/{customer_id}/entries",
    response_model=LedgerEnryResponse,
    status_code=201,
)
def create_ledger_entry(
    customer_id:UUID,
    data:LedgerEntryCreate,
    x_organization_id:UUID = Header(...),
):
    customer = customers.get_customer(
        organization_id=x_organization_id,
        customer_id=customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer Not Found",
        )

    entry = ledger.create_ledger_entry(
        organization_id=x_organization_id,
        customer_id=customer_id,
        entry_type=data.entry_type,
        direction=data.direction,
        amount=data.amount,
        description=data.description
    )

    return entry

@router.get(
    "/customers/{customer_id}/entries",
    response_model=list[LedgerEnryResponse],
)
def list_customer_ledger(
    customer_id:UUID,
    x_organization_id:UUID = Header(...),
):
    entries = get_customer_ledger(
        organization_id=x_organization_id,
        customer_id=customer_id,
    )

    if entries is None:
        raise HTTPException(
            status_code=404,
            detail="Customer Not Found",
        )
    return entries

@router.get(
    "/customers/{customer_id}/balance",
    response_model=CustomerBalanceResponse,
)
def get_balance(
    customer_id:UUID,
    x_organization_id:UUID = Header(...),
):
    balance = get_customer_balance(
        organization_id=x_organization_id,
        customer_id=customer_id,
    )

    if balance is None:
        raise HTTPException(
            status_code=404,
            detail="Customer Not Found",
        )

    return balance