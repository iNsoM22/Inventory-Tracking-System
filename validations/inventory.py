from pydantic import BaseModel, Field, UUID4, ConfigDict
from typing import Optional
from .product import ProductResponseWithCategory


class InventoryBase(BaseModel):
    product_id: UUID4 = Field(..., description="Unique identifier for the Product")
    quantity: int = Field(default=0, ge=0, description="Quantity of the Product in the Inventory")
    max_discount_amount: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Maximum Discount allowed on the product (0-1 scale)"
    )

    model_config = ConfigDict(from_attributes=True)


class InventoryRequest(InventoryBase):
    store_id: UUID4 = Field(..., description="Unique identifier for the Store")



class InventoryResponse(InventoryBase):
    store_id: UUID4 = Field(..., description="Unique identifier for the Store")


class InventoryUpdateRequest(BaseModel):
    product_id: UUID4 = Field(..., description="Unique identifier for the Product")
    quantity: Optional[int] = Field(None, ge=0, description="Updated Quantity of the Product")
    max_discount_amount: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Updated Max Discount Allowed (0-1)"
    )


class InventoryResponseWithProduct(InventoryResponse):
    product: Optional[ProductResponseWithCategory] = Field(
        None, description="Product details including category"
    )
    product_id: UUID4 = Field(exclude=True, description="Unique identifier for the Product")