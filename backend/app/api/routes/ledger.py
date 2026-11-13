from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, Query
from app.db.queries import customers, ledger
from app.schemas.ledger import (
    LedgerEntryCreate,
    LedgerEntryResponse,
    CustomerBalanceResponse,
)
from app.services.ledger import(
    get_customer_balance,
    get_customer_ledger,
)
from app.schemas.common import PaginatedResponse

router = APIRouter(
    prefix = "/ledger",
    tags = ["ledger"],
)

@router.post(
    "/customers/{customer_id}/entries",
    response_model=LedgerEntryResponse,
    status_code=201,
    summary="Create a ledger entry",
    description=(
        "Create a sale, payment, opening balance or adjustment. "
        "Ledger entries are immutable after creation."
    ),
    responses={
        404: {"description": "Customer not found"},
        422: {"description": "Invalid ledger entry"},
    },
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
    response_model=PaginatedResponse[LedgerEntryResponse],
    summary="List customer ledger entries",
    description="Retrieve a paginated ledger history for a customer.",
    responses={
        404: {"description": "Customer not found"},
    },
)
def list_customer_ledger(
    customer_id:UUID,
    x_organization_id:UUID = Header(...),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    entries = get_customer_ledger(
        organization_id=x_organization_id,
        customer_id=customer_id,
        limit=limit,
        offset=offset,
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
    summary="Get customer balance",
    description="Calculate the customer's outstanding balance from ledger entries.",
    responses={
        404: {"description": "Customer not found"},
    },
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