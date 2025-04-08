from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import Optional, Literal
from datetime import datetime, timezone
from .user import UserPublicResponse


class TransactionBase(BaseModel):
    type: Literal["Restock", "Sale", "Refund", "Removal"] = Field(
        ...,
        max_length=10,
        description="Type of Transaction (Restock, Sale, Refund, Removal)"
    )
    date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the transaction occurred"
    )
    operation_id: UUID4 = Field(
        ...,
        description="Associated Operation ID"
    )
    request_made_by: UUID4 = Field(
        ...,
        description="ID of the User which made the Transaction Request"
    )

    model_config = ConfigDict(from_attributes=True)


class TransactionResponseWithOutStore(TransactionBase):
    id: UUID4 = Field(
        ...,
        description="Unique Transaction Identifier"
    )


class TransactionResponse(TransactionBase):
    id: UUID4 = Field(
        ...,
        description="Unique Transaction Identifier"
    )
    store_id: UUID4 = Field(
        ...,
        description="ID of the Store where the transaction occurred"
    )


class TransactionResponseWithRelations(TransactionResponse):
    user: UserPublicResponse = Field(
        None,
        description="Employee handling the transaction"
    )
