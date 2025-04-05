from fastapi import APIRouter, HTTPException
from typing import List
from validations.inventory import InventoryResponse, InventoryResponseWithProduct, InventoryRequest, InventoryUpdateRequest
from utils.db import db_dependency
from schemas.inventory import Inventory
from uuid import UUID


router = APIRouter(prefix="/inventory")

@router.get("/all", response_model=List[InventoryResponse])
async def get_all_inventory(product_details: bool, db: db_dependency):
    """Retrieve all Inventory."""
    try:
        complete_inventory = db.query(Inventory).all()
        if product_details:
            return [InventoryResponseWithProduct.model_validate(inventory) 
                    for inventory in complete_inventory]
            
        return [InventoryResponse.model_validate(inventory) for inventory in complete_inventory]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Records: {str(e)}")



@router.get("/get/{store_id}", response_model=InventoryResponse)
async def get_inventory_by_store(store_id: UUID, product_details: bool, db: db_dependency):
    """Retrieve Inventory for a specific Store."""
    try:
        complete_inventory = db.query(Inventory).filter(Inventory.store_id == store_id).all()
        
        if not complete_inventory:
            raise HTTPException(status_code=404, detail="Inventory Not Found.")
        
        if product_details:
            return [InventoryResponseWithProduct.model_validate(inventory) 
                    for inventory in complete_inventory]
            
        return [InventoryResponse.model_validate(inventory) for inventory in complete_inventory]
         
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Records: {str(e)}")
    
    

@router.post("/add", response_model=InventoryResponse)
async def add_inventory(inventory: InventoryRequest, db: db_dependency):
    """Add a new Inventory Record."""
    try:
        new_inventory = Inventory(**inventory.model_dump())
        db.add(new_inventory)
        db.commit()
        
        db.refresh(new_inventory)
        return InventoryResponse.model_validate(new_inventory)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Adding Record: {str(e)}")
        
        
@router.put("/mod/{store_id}", response_model=List[InventoryResponse])
async def modify_inventory(
    store_id: UUID, update_data: List[InventoryUpdateRequest], db: db_dependency = None
):
    """Update Inventory for a Specific Store."""
    try:
        inventory_records = db.query(Inventory).filter(Inventory.store_id == store_id).all()

        if not inventory_records:
            raise HTTPException(status_code=404, detail="Inventory Not Found.")

        inventory_map = {record.product_id: record for record in inventory_records}
        updated_items = []

        for update in update_data:
            inventory = inventory_map.get(update.product_id)

            if not inventory:
                raise HTTPException(
                    status_code=404, detail=f"Inventory Not Found for Product ID: {update.product_id}")

            if update.quantity is not None:
                inventory.quantity = update.quantity

            if update.max_discount_amount is not None:
                inventory.max_discount_amount = update.max_discount_amount

            updated_items.append(inventory)
            
        db.commit()
        return [InventoryResponse.model_validate(item) for item in updated_items]

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Records: {str(e)}")

    

@router.delete("/del/{store_id}", status_code=204)
async def delete_inventory_by_store(store_id: UUID, product_ids: List[UUID], db: db_dependency):
    """Delete Inventory for a specific Store."""
    try:
        inventory_records = db.query(Inventory).filter(Inventory.store_id == store_id).all()

        if not inventory_records:
            raise HTTPException(status_code=404, detail="Inventory Not Found.")

        inventory_map = {record.product_id: record for record in inventory_records}

        for product_id in product_ids:
            inventory = inventory_map.get(product_id)

            if not inventory:
                raise HTTPException(status_code=404, detail=f"Inventory Not Found for Product ID: {product_id}")

            db.delete(inventory)

        db.commit()

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Records: {str(e)}")

    
    
    
    
# P.S: Modifications and Removal of Inventory Records should be performed through StockRemoval and
# Restock APIs. The Inventory APIs are highly discouraged from usage due to Auditing Issues.