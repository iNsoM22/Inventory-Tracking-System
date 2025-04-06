from pydantic import BaseModel, Field, UUID4, ConfigDict, computed_field
from typing import Optional, List, Literal
from datetime import datetime, timezone, timedelta
from .product import ProductResponseWithCategory
from schemas.order import Order


class RefundItemBase(BaseModel):
    product_id: UUID4 = Field(..., description="Unique identifier for the Product")
    quantity: int = Field(gt=0, description="Quantity of the Product in the Cart")

    model_config = ConfigDict(from_attributes=True)


class RefundItemRequest(RefundItemBase):
    pass


class RefundItemResponse(RefundItemBase):
    product: Optional[ProductResponseWithCategory] = Field(None, description="Product Details")
    product_id: UUID4 = Field(exclude=True, description="Unique identifier for the Product")
    


class RefundBase(BaseModel):
    store_id: UUID4 = Field(..., description="Store ID")
    reason: Optional[str] = Field(None, description="Reason for the Refund")
    application_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone), description="Timestamp When the Request for Refund is Placed")
    date_refunded: Optional[datetime] = Field(default=None, description="Timestamp When the Refund is Successful")
    status: Optional[
        Literal["Pending",
                "Approved",
                "Cancelled",
                "Rejected",
                "Refunded"]
        ] = Field(default="Pending", 
            description="Application Status. Can be Pending, Approved, Rejected, Cancelled or Refunded.")
    
    amount: Optional[float] = Field(gt=0, description="Amout of the Refund")
    order_id: UUID4 = Field(..., description="Unique identifier for the Order")
    items: List[RefundItemBase] = Field(strict=True, description="List of Items to Refund")

    model_config = ConfigDict(from_attributes=True)


class RefundRequest(RefundBase):
    
    def validate_application(self, order: Order):
        err_occured = False
        if order.status == "Cancelled":
            err_occured = True
            raise ValueError("Order is Already been Cancelled")
        
        if order.status == "Pending":
            err_occured = True
            raise ValueError("Order Must be Delivered for the Refund")
        
        
        products_for_refund_dict = {p.id: p for p in self.items}
        for item in order.items:
            if item.product_id not in products_for_refund_dict:
                err_occured = True
                raise ValueError(f"Product {item.product_id} is not Found in the Order")
            
            ordered_product = products_for_refund_dict[item.product_id]
            
            if item.quantity > ordered_product.quantity:
                err_occured = True
                raise ValueError(f"Quantity of Product  {ordered_product.name} is more than the Ordered Amount.")
        
        if self.application_date - order.date_received > timedelta(days=15):
            err_occured = True
            raise Exception("Refund Application is too Late") 
        
        self.status = "Approved" if not err_occured else "Rejected"
            
            
class RefundUpdateRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Reason for the Refund")
    status: Optional[
        Literal["Pending",
                "Approved",
                "Cancelled",
                "Rejected",
                "Refunded"]
        ] = Field(default=None, 
            description="Application Status. Can be Pending, Approved, Rejected, Cancelled or Refunded.")
    
    @computed_field
    @property
    def date_refunded(self) -> datetime | None:
        if self.status == "Refunded":
            return datetime.now(timezone.utc)
        return None
    

class RefundResponse(RefundBase):
    id: UUID4 = Field(..., description="Unique identifier for the Order")
    items: List[RefundItemResponse] = Field(default=list, description="List of Items to Refund")


class RefundResponseWithOutStore(RefundResponse):
    store_id: UUID4 = Field(exclude=True, description="Store ID")