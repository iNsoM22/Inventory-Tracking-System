from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from utils.db import db_dependency
from validations.removal import StockRemovalRequest, StockRemovalResponse, StockRemovalUpdateRequest
from schemas.inventory import Inventory
from schemas.removal import StockRemoval, RemovalItems
from utils.stock_restore import restore_inventory


router = APIRouter(prefix="/stock-removals", tags=["Stock Removals"])


@router.post("/add", response_model=StockRemovalResponse)
def create_stock_removal(removal_data: StockRemovalRequest, db: db_dependency):
    try:
        product_ids = [item.product_id for item in removal_data.items]
        inventories = {
            inv.product_id: inv
            for inv in db.query(Inventory).filter(
                Inventory.store_id == removal_data.store_id,
                Inventory.product_id.in_(product_ids)
            ).all()
        }

        removal_items = []

        for item in removal_data.items:
            inventory = inventories.get(item.product_id)
            if not inventory:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} Not Found in Inventory.")

            if inventory.quantity < item.removal_quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient Quantity for Product {item.product_id}. Available: {inventory.quantity}"
                )

            inventory.quantity -= item.removal_quantity

            removal_item = RemovalItems(
                product_id=item.product_id,
                previous_quantity=item.previous_quantity,
                removal_quantity=item.removal_quantity)
            
            removal_items.append(removal_item)

        stock_removal = StockRemoval(
            store_id=removal_data.store_id,
            removal_reason=removal_data.removal_reason,
            date=removal_data.date,
            is_cancelled=removal_data.is_cancelled,
            items=removal_items)

        db.add(stock_removal)
        db.commit()
        db.refresh(stock_removal)

        return StockRemovalResponse.model_validate(stock_removal)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Creating Stock Removal: {str(e)}")
    


@router.get("/get/{removal_id}", response_model=StockRemovalResponse)
def get_stock_removal(removal_id: UUID, db: db_dependency):
    try:
        stock_removal = db.query(StockRemoval).filter(StockRemoval.id == removal_id).first()
        if not stock_removal:
            raise HTTPException(status_code=404, detail="Stock Removal not found.")
        return StockRemovalResponse.model_validate(stock_removal)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Stock Removal Records: {str(e)}")


@router.get("/all", response_model=List[StockRemovalResponse])
def get_stock_removals(db: db_dependency, limit: int = 10, offset: int = 0):
    try:
        removals = db.query(StockRemoval).offset(offset).limit(limit).all()
        return [StockRemovalResponse.model_validate(r) for r in removals]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Stock Removal Records: {str(e)}")



@router.put("/mod/{removal_id}", response_model=StockRemovalResponse)
def update_stock_removal(removal_id: UUID, update_data: StockRemovalUpdateRequest, db: db_dependency):
    stock_removal = db.query(StockRemoval).filter(StockRemoval.id == removal_id).first()
    if not stock_removal:
        raise HTTPException(status_code=404, detail="Stock Removal Record Not Found.")

    if update_data.removal_reason is not None:
        stock_removal.removal_reason = update_data.removal_reason
    if update_data.date is not None:
        stock_removal.date = update_data.date
    if update_data.is_cancelled is not None:
        stock_removal.is_cancelled = update_data.is_cancelled
    
    if update_data.is_cancelled:
        products = {p.id: p.removal_quantity for p in stock_removal.items}
        restore_inventory(db, products, add_stock=True)
    
    db.commit()
    db.refresh(stock_removal)
    return StockRemovalResponse.model_validate(stock_removal)


@router.delete("/del/{removal_id}", status_code=204)
def delete_stock_removal(removal_id: UUID, db: db_dependency):
    stock_removal = db.query(StockRemoval).filter(StockRemoval.id == removal_id).first()
    if not stock_removal:
        raise HTTPException(status_code=404, detail="Stock Removal not found.")
    
    products = {p.id: p.removal_quantity for p in stock_removal.items}
    restore_inventory(db, products, add_stock=True)

    db.delete(stock_removal)
    db.commit()
    return {"detail": "Stock Removal and related Inventory Items have been deleted Successfully."}


# P.S: Deletion of Stock Removal is highly discouraged, instead Use the Update API to Cancel the operation.
# Also, Once Removed Application is submitted the Items Cannot be Changed.