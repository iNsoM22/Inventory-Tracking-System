from fastapi import APIRouter, HTTPException
from typing import List, Literal
from sqlalchemy.orm import joinedload
from schemas.transaction import Transaction
from schemas.store import Store
from schemas.order import Order, CartItems
from schemas.refund import Refund
from validations.store import (
    TransactionResponseWithRelations, 
    TransactionResponse, 
    StoreBase,
    StoreRequest, 
    StoreResponse, 
    StoreResponseWithRelations, 
    StoreUpdateRequest)
from utils.db import db_dependency
from uuid import UUID
from validations.order import OrderResponse


include_details = Literal["employees", "inventory", "transactions", "restocks", "removals"]
router = APIRouter(prefix="/stores")

@router.post("/add", response_model=List[StoreResponse])
async def create_store(stores: List[StoreRequest], db: db_dependency):
    """Create a New Store."""
    try:
        new_stores = [Store(**store.model_dump()) for store in stores]
        db.add_all(new_stores)
        db.commit()
        return StoreResponse.model_validate_many(new_stores)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Creating Stores: {str(e)}")
    


@router.get("/all", response_model=List[StoreResponse])
async def get_stores(db: db_dependency):
    """Get All Stores along with their related transactions."""
    try:
        stores = db.query(Store).all()
        return [StoreResponse.model_validate(store) for store in stores]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Stores: {str(e)}")
    
    

@router.get("/get/{store_id}", response_model=StoreResponseWithRelations)
async def get_store_by_id(store_id: UUID,
                          db: db_dependency, 
                          include_employees=False, 
                          include_inventory=False, 
                          include_transactions=False, 
                          include_restocks=False, 
                          include_removals=False,
                          include_orders=False,
                          include_refunds=False):
    """Get a Stores along with its Related Information using Store ID."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        return StoreResponseWithRelations.include_related_information(store, 
                                                                      include_employees=include_employees,
                                                                      include_inventories=include_inventory,
                                                                      include_transactions=include_transactions,
                                                                      include_restocks=include_restocks,
                                                                      include_removals=include_removals,
                                                                      include_orders=include_orders,
                                                                      include_refunds=include_refunds)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Store: {str(e)}")
    


@router.put("/update/{store_id}", response_model=StoreResponse)
async def update_store(store_id: UUID, store: StoreUpdateRequest, db: db_dependency):
    """Update a Store."""
    try:
        store_to_update = db.query(Store).filter(Store.id == store_id).first()
        if not store_to_update:
            raise HTTPException(status_code=404, detail="Store Not Found")
        
        if store.name:
            store_to_update.name = store.name
        if store.location_id:
            store_to_update.location_id = store.location_id
            
        db.commit()
        db.refresh(store_to_update)
        return StoreResponse.model_validate(store_to_update)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Store: {str(e)}")
    
    


@router.delete("/del/{store_id}", status_code=204)
async def delete_store(store_id: UUID, db: db_dependency):
    """Delete a Store by ID."""
    try:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store Not Found")
        
        db.delete(store)
        db.commit()
        return {"detail": "Store Deleted Successfully."}
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Store: {str(e)}")