import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CustomerCreate(BaseModel):
    name:str = Field(min_length=1, max_length=150)
    phone:str|None = Field(default=None, max_length=20,)
    email:EmailStr|None=None
    address:str|None=Field(default=None, max_length=500)

class customerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:uuid.UUID
    organization_id:uuid.UUID
    name:str
    phone:str|None
    email:str|None
    address:str|None
    created_at:datetime