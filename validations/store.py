from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from .location import LocationBase
from .employee import EmployeeResponseWithOutStore
from .inventory import InventoryBase
from .restock import RestockResponseWithOutStore
from .removal import StockRemovalResponseWithOutStore
from .order import OrderResponseWithOutStore
from .refund import RefundResponseWithOutStore
from .transaction import TransactionResponseWithOutStore


class StoreBase(BaseModel):
    name: str = Field(
        ...,
        max_length=50,
        description="Name of the Store"
    )

    location_id: int = Field(
        ...,
        description="Unique identifier for the Location"
    )

    model_config = ConfigDict(from_attributes=True)


class StoreRequest(StoreBase):
    pass


class StoreWithIncludeRelationsRequest(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the Store"
    )
    inlcude_inventory: bool = Field(
        False,
        description="Include Inventory in the response"
    )
    include_employee: bool = Field(
        False,
        description="Include Employee in the response"
    )
    include_restock: bool = Field(
        False,
        description="Include Restock in the response"
    )
    include_removal: bool = Field(
        False,
        description="Include Removal in the response"
    )
    include_order: bool = Field(
        False,
        description="Include Order in the response"
    )
    include_refund: bool = Field(
        False,
        description="Include Refund in the response"
    )
    include_transactions: bool = Field(
        False,
        description="Include Transactions in the response"
    )
    records_limit: int = Field(
        100,
        description="Number of records to return in the response"
    )
    inventory_offset: int = Field(
        0,
        description="Offset for Inventory in the response"
    )
    employee_offset: int = Field(
        0,
        description="Offset for Employee in the response"
    )
    restock_offset: int = Field(
        0,
        description="Offset for Restock in the response"
    )
    removal_offset: int = Field(
        0,
        description="Offset for Removal in the response"
    )
    order_offset: int = Field(
        0,
        description="Offset for Order in the response"
    )
    refund_offset: int = Field(
        0,
        description="Offset for Refund in the response"
    )
    transactions_offset: int = Field(
        0,
        description="Offset for Transactions in the response"
    )


class StoreUpdateRequest(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Updated Store Name"
    )

    location_id: Optional[int] = Field(
        None,
        gt=0,
        description="Updated Location ID"
    )


class StoreResponse(StoreBase):
    id: int = Field(
        ...,
        description="Unique identifier for the Store"
    )


class StoreResponseWithRelations(StoreResponse):
    location_id: int = Field(
        exclude=True,
        gt=0,
        description="Unique identifier for the Location"
    )
    location: Optional[LocationBase] = Field(
        None,
        description="Store Location Details"
    )
    employees: Optional[List[EmployeeResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Store Employees"
    )
    inventory: Optional[List[InventoryBase]] = Field(
        default_factory=list,
        description="List of Inventory Items"
    )
    restocks: Optional[List[RestockResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Restock Orders"
    )
    removals: Optional[List[StockRemovalResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Stock Removals"
    )
    transactions: Optional[List[TransactionResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Store Transactions"
    )
    orders: Optional[List[OrderResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Store Orders"
    )
    refunds: Optional[List[RefundResponseWithOutStore]] = Field(
        default_factory=list,
        description="List of Store Refunds"
    )
