from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import Optional, List, Literal
from datetime import datetime


class RemovalItemBase(BaseModel):
    product_id: UUID4 = Field(..., description="Product ID")
    previous_quantity: int = Field(..., ge=0, description="Previous product quantity")
    removal_quantity: int = Field(..., gt=0, description="Quantity to remove")

    model_config = ConfigDict(from_attributes=True)


class RemovalItemRequest(RemovalItemBase):
    pass



class RemovalItemResponse(RemovalItemBase):
    removal_id: UUID4 = Field(..., description="Stock Removal Operation ID")


class RemovalItemUpdateRequest(BaseModel):
    product_id: UUID4 = Field(..., description="Product ID")
    previous_quantity: Optional[int] = Field(..., ge=0, description="Previous product quantity")
    removal_quantity: Optional[int] = Field(..., gt=0, description="Quantity to remove")

    model_config = ConfigDict(from_attributes=True)


class StockRemovalBase(BaseModel):
    removal_reason: Literal["Damaged",
                            "Lost",
                            "Internal Use",
                            "Adjustment",
                            "Return To Supplier"] = Field(..., description="Removal Resaon. Can be Expired, Damaged, Lost, Internal Use, Return to Supplier, or Adjustment")
    date: Optional[datetime] = Field(None, description="Timestamp of the removal")
    is_cancelled: Optional[bool] = Field(False, description="Whether the Removal is Cancelled or Not")
    items: List[RemovalItemBase] = Field(default_factory=list, description="List of Removed Items")

    model_config = ConfigDict(from_attributes=True)



class StockRemovalRequest(StockRemovalBase):
    store_id: UUID4 = Field(..., description="Store ID")
    is_cancelled: bool = False


class StockRemovalUpdateRequest(BaseModel):
    id: UUID4 = Field(..., description="Stock Removal ID")
    removal_reason: Optional[
        Literal["Damaged",
                "Lost",
                "Internal Use",
                "Adjustment",
                "Return To Supplier"]] = Field(default=None, description="Removal Resaon. Can be Expired, Damaged, Lost, Internal Use, Return to Supplier, or Adjustment")
    date: Optional[datetime] = Field(None, description="Timestamp of the removal")
    is_cancelled: Optional[bool] = Field(None, description="Whether the Removal is Cancelled or Not")


class StockRemovalResponseWithOutStore(StockRemovalBase):
    id: UUID4 = Field(..., description="Stock Removal ID")


class StockRemovalResponse(StockRemovalBase):
    id: UUID4 = Field(..., description="Stock Removal ID")
    store_id: UUID4 = Field(..., description="Store ID")
