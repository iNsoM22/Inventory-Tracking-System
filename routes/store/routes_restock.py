from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from utils.db import db_dependency
from validations.inventory import InventoryRequest
from validations.restock import RestockRequest, RestockResponse, RestockUpdateRequest
from schemas.product import Product
from schemas.restock import Restock, RestockItems
from schemas.inventory import Inventory
from utils.stock_restore import restore_inventory


router = APIRouter(prefix="/restocks", tags=["Restocks"])


@router.post("/add", response_model=RestockResponse)
def create_restock(restock_data: RestockRequest, db: db_dependency):
    product_ids = [item.product_id for item in restock_data.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}
    
    products_in_store_inventory = {p.product_id: p for p in db.query(Inventory).filter(Inventory.store_id == restock_data.store_id).all()}
    
    if len(products) != len(product_ids):
        raise HTTPException(status_code=404, detail="One or More Products not found.")

    restock_items = []
    new_inventory_records = []

    for item in restock_data.items:
        product_in_store_inventory = products_in_store_inventory.get(item.product_id, None)
        
        if not product_in_store_inventory:
            new_inventory = Inventory(
                **InventoryRequest(
                    product_id=item.product_id,
                    quantity=item.restock_quantity,
                    store_id=restock_data.store_id,
                    max_discount_amount=0,
                ).model_dump()
            )
            new_inventory_records.append(new_inventory)
        
        else:
            restock_item = RestockItems(
                product_id=item.product_id,
                previous_quantity=product_in_store_inventory.quantity if product_in_store_inventory.quantity else 0,
                restock_quantity=item.restock_quantity)
            
            restock_items.append(restock_item)
            product_in_store_inventory.quantity += item.restock_quantity

    new_restock = Restock(
        store_id=restock_data.store_id,
        status=restock_data.status,
        date_placed=restock_data.date_placed,
        date_received=restock_data.date_received,
        items=restock_items)
    
    if len(new_inventory_records):
        db.add_all(new_inventory_records)
    
    db.add(new_restock)
    db.commit()
    db.refresh(new_restock)

    return RestockResponse.model_validate(new_restock)


@router.get("/get/{restock_id}", response_model=RestockResponse)
def get_restock(restock_id: UUID, db: db_dependency):
    try:
        restock = db.query(Restock).filter(Restock.id == restock_id).first()
        if not restock:
            raise HTTPException(status_code=404, detail="Restock not found.")
        return RestockResponse.model_validate(restock)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Restock Records: {str(e)}")
    
    
@router.get("/all", response_model=List[RestockResponse])
def get_restocks(db: db_dependency, limit: int = 10, offset: int = 0):
    try:
        restocks = db.query(Restock).offset(offset).limit(limit).all()
        return [RestockResponse.model_validate(r) for r in restocks]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Restock Records: {str(e)}")
    

@router.put("/mod/{restock_id}", response_model=RestockResponse)
def update_restock(restock_id: UUID, new_data: RestockUpdateRequest, db: db_dependency):
    try:
        restock = db.query(Restock).filter(Restock.id == restock_id).first()
        if not restock:
            raise HTTPException(status_code=404, detail="Restock Order Not Found.")
        
        if new_data.status is not None:
            restock.status = new_data.status
        if new_data.date_received is not None:
            restock.date_received = new_data.date_received
        
        if new_data.status == "Cancelled":
            products = {p.id: p.restock_quantity for p in restock.items}
            restore_inventory(db, products, add_stock=False)

        db.commit()
        db.refresh(restock)
        return RestockResponse.model_validate(restock)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Restock: {str(e)}")


@router.delete("/del/{restock_id}", status_code=204)
def delete_restock(restock_id: UUID, db: db_dependency):
    try:
        restock = db.query(Restock).filter(Restock.id == restock_id).first()
        if not restock:
            raise HTTPException(status_code=404, detail="Restock Record Not Found.")
        
        products = {p.id: p.restock_quantity for p in restock.items}
        restore_inventory(db, products, add_stock=False)
        
        db.delete(restock)
        db.commit()
        return {"detail": "Restock Record Deleted Successfully."}
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Restock: {str(e)}")
