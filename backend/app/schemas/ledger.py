import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, model_validator, Field

EntryType = Literal[
    "sale",
    "payment",
    "opening_balance",
    "adjustment",
]

EntryDirection = Literal["debit","credit"]

class LedgerEntryCreate(BaseModel):
    entry_type:EntryType
    direction:EntryDirection
    amount:Decimal = Field(gt=0, max_digits=12, decimal_places=2,)
    description:str|None=Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_direction(self):
        if(
            self.entry_type in ("sale","opening_balance")
            and self.direction != "debit"
        ):
            raise ValueError(
                f"{self.entry_type} must be debit"
            )

        if (
            self.entry_type == "payment"
            and self.direction != "credit"
        ):
            raise ValueError("payment must be a credit")

        return self

class LedgerEnryResponse(BaseModel):
    id:uuid.UUID
    customer_id:uuid.UUID
    entry_type:EntryType
    direction:EntryDirection
    amount:Decimal
    description:str|None
    created_at:datetime

class CustomerBalanceResponse(BaseModel):
    customer_id: uuid.UUID
    total_debit: Decimal
    total_credit: Decimal
    outstanding_balance: Decimal