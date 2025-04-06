from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import Optional, List
from schemas.store import Store
from datetime import datetime
from .location import LocationBase
from .employee import EmployeeBase
from .inventory import InventoryBase
from .restock import RestockBase
from .removal import StockRemovalBase

class TransactionBase(BaseModel):
    type: str = Field(..., max_length=50, description="Type of Transaction (Restock, Sale, Refund, Removal)")
    operation_id: UUID4 = Field(..., description="Associated Operation ID")
    handler_id: UUID4 = Field(..., description="ID of the Employee handling the transaction")
    store_id: UUID4 = Field(..., description="ID of the Store where the transaction occurred")
    date: Optional[datetime] = Field(None, description="Timestamp of when the transaction occurred")

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(TransactionBase):
    id: UUID4 = Field(..., description="Unique Transaction Identifier")
    store_id: UUID4 = Field(..., description="ID of the Store where the transaction occurred")


class TransactionResponseWithRelations(TransactionResponse):
    handler: Optional[EmployeeBase] = Field(None, description="Employee handling the transaction")
    store: Optional["StoreBase"] = Field(None, description="Store where the transaction took place")



class StoreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Name of the Store")
    location_id: int = Field(..., gt=0, description="Unique identifier for the Location")

    model_config = ConfigDict(from_attributes=True)


class StoreCreateRequest(StoreBase):
    pass


class StoreUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Updated Store Name")
    location_id: Optional[int] = Field(None, gt=0, description="Updated Location ID")



class StoreResponse(StoreBase):
    id: int = Field(..., description="Unique identifier for the Store")



class StoreResponseWithRelations(StoreResponse):
    location: Optional[LocationBase] = Field(None, description="Store Location Details")
    employees: Optional[List[EmployeeBase]] = Field(default_factory=list, description="List of Store Employees")
    inventory: Optional[List[InventoryBase]] = Field(default_factory=list, description="List of Inventory Items")
    restocks: Optional[List[RestockBase]] = Field(default_factory=list, description="List of Restock Orders")
    removals: Optional[List[StockRemovalBase]] = Field(default_factory=list, description="List of Stock Removals")
    transactions: Optional[List[TransactionBase]] = Field(default_factory=list, description="List of Store Transactions")
    
    
    @classmethod
    def include_related_information(
                                    cls,
                                    store_object: Store,
                                    include_location=True,
                                    include_inventories=True,
                                    include_employees=False,
                                    include_transactions=False,
                                    include_restocks=False,
                                    include_removals=False):
    
        return cls(
            id=store_object.id,
            name=store_object.name,
            location_id=store_object.location_id,
            location=LocationBase(store_object.location) if include_location and store_object.location else None,
            inventory=[InventoryBase.model_validate(item) for item in store_object.inventory] if include_inventories else [],
            employees=[EmployeeBase.model_validate(emp) for emp in store_object.employees] if include_employees else [],
            restocks=[RestockBase.model_validate(r) for r in store_object.restocks] if include_restocks else [],
            removals=[StockRemovalBase.model_validate(rm) for rm in store_object.removals] if include_removals else [],
            transactions=[TransactionBase.model_validate(tx) for tx in store_object.transactions] if include_transactions else [],
         )