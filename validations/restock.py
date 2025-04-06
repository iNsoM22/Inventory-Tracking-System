from pydantic import BaseModel, Field, UUID4, ConfigDict, computed_field, UUID4
from typing import Optional, List, Literal
from datetime import datetime, timezone
from .product import ProductResponseWithCategory


class RestockItemBase(BaseModel):
    product_id: UUID4 = Field(..., description="Unique identifier for the Product")
    previous_quantity: int = Field(ge=0, description="Quantity of the Product before Restock")
    restock_quantity: int = Field(gt=0, description="Quantity of the Product to be Restocked")

    model_config = ConfigDict(from_attributes=True)


class RestockItemRequest(RestockItemBase):
    pass


class RestockItemResponse(RestockItemBase):
    restock_id: UUID4 = Field(..., description="Restock ID")
    product: ProductResponseWithCategory = Field(..., description="Product Details")
    product_id: UUID4 = Field(exclude=True, description="Unique identifier for the Product")



class RestockBase(BaseModel):
    status: Literal["Pending", "Completed", "Cancelled"] = Field(
        default="Pending",
        description="Restock Status. Can be Pending, Completed or Cancelled")
    
    date_placed: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp When the Restock Order is Placed")
    
    date_received: Optional[datetime] = Field(
        default=None,
        description="Timestamp When the Restock Order is Delivered")
    
    items: List[RestockItemRequest] = Field(strict=True, min_length=1, description="List of Items to be Restocked")

    model_config = ConfigDict(from_attributes=True)


class RestockRequest(RestockBase):
    store_id: UUID4 = Field(..., description="Store Identifier where the Employee Works")
    


class RestockUpdateRequest(BaseModel):
    id: UUID4 = Field(..., description="Unique identifier for the Order")
    status: Optional[Literal["Pending", "Completed", "Cancelled"]] = Field(
        default=None,
        description="Update the status of the restock order")

    @computed_field
    @property
    def date_received(self) -> Optional[datetime]:
        if self.status == "Completed":
            return datetime.now(timezone.utc)
        return None


class RestockResponse(RestockBase):
    id: UUID4 = Field(..., description="Unique identifier for Restock")
    store_id: UUID4 = Field(..., description="Store Identifier where the Employee Works")
    items: List[RestockItemResponse] = Field(default=list, description="List of Restocked Items")
