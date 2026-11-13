from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, Query
from app.db.queries import customers, organizations
from app.schemas.customer import(
    CustomerCreate,
    CustomerResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter(
    prefix = "/customers",
    tags=["Customers"],
)

@router.post(
    "/",
    response_model = CustomerResponse,
    status_code=201,
    summary="Create a customer",
    description="Create a customer under the specified organization.",
    responses={
        404: {"description": "Organization not found"},
        422: {"description": "Invalid customer input"},
    },
)
def create_customer(
    data:CustomerCreate,
    x_organization_id:UUID = Header(...),
):
    organization = organizations.get_organization(
        organization_id=x_organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code = 404,
            detail = "Organization not found",
        )
    
    customer = customers.create_customer(
        organization_id=x_organization_id,
        name=data.name,
        phone=data.phone,
        email=str(data.email) if data.email else None,
        address=data.address,
    )

    return customer

@router.get(
    "/",
    response_model = PaginatedResponse[CustomerResponse],
    summary="List customers",
    description="Retrieve a paginated list of customers belonging to an organization.",
)
def list_customers(
    x_organization_id: UUID = Header(...), 
    limit: int = Query(default=20, ge=1, le=100), 
    offset: int = Query(default=0, ge=0),
):
    return customers.get_customers(
        organization_id = x_organization_id,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get a customer",
    responses={
        404: {"description": "Customer not found"},
    },
)
def get_customer(
    customer_id:UUID,
    x_organization_id:UUID=Header(...),
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

    return customer