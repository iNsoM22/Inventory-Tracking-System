from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from schemas.store import Store
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

    @classmethod
    def include_related_information(
        cls,
        store_object: Store,
        include_inventories: bool = True,
        include_employees: bool = False,
        include_transactions: bool = False,
        include_restocks: bool = False,
        include_removals: bool = False,
        include_orders: bool = False,
        include_refunds: bool = False
    ):

        return cls(
            id=store_object.id,
            name=store_object.name,
            location_id=store_object.location_id,
            location=LocationBase(store_object.location),

            inventory=[
                InventoryBase.model_validate(item)
                for item in store_object.inventory
            ] if include_inventories else [],

            employees=[
                EmployeeResponseWithOutStore.model_validate(emp)
                for emp in store_object.employees
            ] if include_employees else [],

            restocks=[
                RestockResponseWithOutStore.model_validate(r)
                for r in store_object.restocks
            ] if include_restocks else [],

            removals=[
                StockRemovalResponseWithOutStore.model_validate(rm)
                for rm in store_object.removals
            ] if include_removals else [],

            transactions=[
                TransactionResponseWithOutStore.model_validate(tx)
                for tx in store_object.transactions
            ] if include_transactions else [],

            orders=[
                OrderResponseWithOutStore.model_validate(order)
                for order in store_object.orders
            ] if include_orders else [],

            refunds=[
                RefundResponseWithOutStore.model_validate(ref)
                for ref in store_object.refunds
            ] if include_refunds else []
        )
