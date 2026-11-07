from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.db.queries import organizations
from app.schemas.organization import(OrganizationCreate,OrganizationResponse,)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizaations"],
)

@router.post(
    '/',
    response_model = OrganizationResponse,
    status_code=201,
)

def create_organization(data:OrganizationCreate):

    organization = organizations.create_organization(name=data.name)

    return organization

@router.get(
    "/{organization_id}",
    response_model = OrganizationResponse,
)

def get_organization(organization_id:UUID):
    organization = organizations.get_organization(
        organization_id=organization_id
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )