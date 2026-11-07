from uuid import UUID
from fastapi import APIRouter, Header, HTTPException
from app.db.queries import customers, organizations
from app.schemas.customer import(
    CustomerCreate,
    customerResponse,
)

router = APIRouter(
    prefix = "/customers",
    tags=["Customers"],
)

@router.post(
    "/",
    response_model = customerResponse,
    status_code=201,
)
def create_csutomer(
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
    response_model = list[customerResponse]
)
def list_customers(
    x_organization_id: UUID = Header(...),
):
    return customers.get_customers(
        organization_id = x_organization_id
    )

@router.get(
    "/{customer_id}",
    response_model=customerResponse
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