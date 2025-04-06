from pydantic import BaseModel, Field, UUID4, ConfigDict, model_validator, computed_field    
from typing import Optional, List, Literal
from datetime import datetime, timezone
from .product import ProductResponseWithCategory
from .customer import CustomerResponse


class CartItemBase(BaseModel):
    product_id: UUID4 = Field(..., description="Unique identifier for the Product")
    quantity: int = Field(gt=0, description="Quantity of the Product in the Cart")
    discount: float = Field(0.0, description="Product Discount Rate (0-1)")

    model_config = ConfigDict(from_attributes=True)


class CartItemUpdateRequest(CartItemBase):
    quantity: Optional[int] = Field(None, ge=0, description="Updated Quantity of the Product in the Cart")
    discount: Optional[float] = Field(None, ge=0, description="Updated Discount Rate of the Product in the Cart")
    


class CartItemResponse(CartItemBase):
    product: Optional[ProductResponseWithCategory] = Field(None, description="Product Details")
    product_id: UUID4 = Field(exclude=True, description="Unique identifier for the Product")



class OrderBase(BaseModel):
    order_amount: float = Field(gt=0, description="Price of the Order")
    store_id: UUID4 = Field(..., description="Store Identifier where the Employee Works")
    discount_amount: float = Field(ge=0, description="Discounted Amount of the Order")
    tax: float = Field(ge=0, description="Tax Amount applied to the Order")
    status: Literal["Pending",
                    "Received",
                    "Cancelled",
                    "For Refund",
                    "Refunded"] = Field(default="Pending", 
                              description="Order status. Can be Pending, Received, Cancelled, For Refund, or Refunded")
    date_placed: Optional[datetime] = Field(default=None, description="Timestamp When the Order is Placed")
    date_received: Optional[datetime] = Field(default=None, description="Timestamp When the Order is Delivered to the Customer")
    order_mode: Literal["Online", "Offline"] = Field(default="Offline", description="Order mode, either Online or Offline")
    order_delivery_address: Optional[str] = Field(None, description="Delivery Address of the Customer")
    customer_id: UUID4 = Field(..., description="Unique identifier for the Customer")
    items: List[CartItemBase] = Field(strict=True, description="List of Cart Items in the Order")


    model_config = ConfigDict(from_attributes=True)
    
         
class OrderRequest(OrderBase):
    @model_validator(mode="after")
    def validate_address(self):
        if self.order_mode == "Online" and not len(self.order_delivery_address):
            raise ValueError("Delivery Address is required for Online Orders")
        return self 


class OrderUpdateRequest(BaseModel):
    status: Literal["Pending",
                    "Received",
                    "Cancelled",
                    "For Refund",
                    "Refunded"] = Field(default="Pending", 
                              description="Order status. Can be Pending, Received, Cancelled, For Refund, or Refunded")

    @computed_field
    @property
    def date_received(self) -> datetime | None:
        if self.status == "Received":
            return datetime.now(timezone.utc)
        return None
        

class OrderResponse(OrderBase):
    id: UUID4 = Field(..., description="Unique identifier for the Order")
    items: List[CartItemResponse] = Field(..., description="List of Cart items in the order")
    customer_id: UUID4 = Field(exclude=True, description="Unique identifier for the Customer")


class OrderResponseWithOutStore(OrderResponse):
    store_id: UUID4 = Field(exclude=True, description="Store Identifier where the Employee Works")
    


class OrderResponseWithCustomer(OrderResponse):
    customer: Optional[CustomerResponse] = Field(None, description="Customer details")  
    