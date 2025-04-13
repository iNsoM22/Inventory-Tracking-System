from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated, Optional
from uuid import UUID
from datetime import date
from utils.db import db_dependency
from validations.removal import StockRemovalRequest, StockRemovalResponse, StockRemovalUpdateRequest
from schemas.inventory import Inventory
from schemas.removal import StockRemoval, RemovalItems
from utils.stock_restore import restore_inventory
from utils.auth import require_access_level
from utils.create_transaction import add_transaction


router = APIRouter(prefix="/stock-removals", tags=["Stock Removals"])


@router.post("/add",
             response_model=StockRemovalResponse,
             status_code=status.HTTP_201_CREATED)
def create_stock_removal(removal_data: StockRemovalRequest,
                         db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(2))]):
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
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Product {item.product_id} Not Found in Inventory")

            if inventory.quantity < item.removal_quantity:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
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

        add_transaction(stock_removal, current_user["id"], db)
        db.add(stock_removal)
        db.commit()
        db.refresh(stock_removal)

        return StockRemovalResponse.model_validate(stock_removal)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Creating Stock Removal: {str(e)}")


@router.get("/get/{removal_id}",
            response_model=StockRemovalResponse,
            status_code=status.HTTP_200_OK)
def get_stock_removal(removal_id: UUID,
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(require_access_level(2))]):
    try:
        stock_removal = db.query(StockRemoval).filter(
            StockRemoval.id == removal_id).first()
        if not stock_removal:
            raise HTTPException(
                status_code=404, detail="Stock Removal not found.")
        return StockRemovalResponse.model_validate(stock_removal)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Stock Removal Records: {str(e)}")


@router.get("/all", response_model=List[StockRemovalResponse])
def get_stock_removals(db: db_dependency,
                       current_user: Annotated[dict, Depends(require_access_level(2))],
                       limit: int = 10, offset: int = 0):
    try:
        removals = db.query(StockRemoval).offset(offset).limit(limit).all()
        return [StockRemovalResponse.model_validate(r) for r in removals]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Stock Removal Records: {str(e)}")


@router.get("/filter",
            response_model=List[StockRemovalResponse],
            status_code=status.HTTP_200_OK)
def filter_stock_removals(db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(2))],
                          store_id: Optional[UUID] = None,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          is_cancelled: Optional[bool] = None,
                          limit: int = 50,
                          offset: int = 0):
    try:
        query = db.query(StockRemoval)
        if store_id:
            query = query.filter(StockRemoval.store_id == store_id)

        if start_date:
            query = query.filter(StockRemoval.date >= start_date)

        if end_date:
            query = query.filter(StockRemoval.date <= end_date)

        if is_cancelled is not None:
            query = query.filter(StockRemoval.is_cancelled == is_cancelled)

        removals = query.offset(offset).limit(limit).all()
        return [StockRemovalResponse.model_validate(r) for r in removals]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Filtering Stock Removals: {str(e)}")


@router.put("/mod/{removal_id}",
            response_model=StockRemovalResponse,
            status_code=status.HTTP_202_ACCEPTED)
def update_stock_removal(removal_id: UUID,
                         update_data: StockRemovalUpdateRequest,
                         db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(3))]):
    try:
        stock_removal = db.query(StockRemoval).filter(
            StockRemoval.id == removal_id).first()
        if not stock_removal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Stock Removal Record Not Found")

        if update_data.removal_reason is not None:
            stock_removal.removal_reason = update_data.removal_reason
        if update_data.date is not None:
            stock_removal.date = update_data.date
        if update_data.is_cancelled is not None:
            stock_removal.is_cancelled = update_data.is_cancelled

        if update_data.is_cancelled:
            products = {
                p.product_id: p.removal_quantity for p in stock_removal.items}
            restore_inventory(db, products, add_stock=True)

        db.commit()
        db.refresh(stock_removal)
        return StockRemovalResponse.model_validate(stock_removal)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Error Occurred While Updating the Stock Removal Application")


@router.delete("/del/{removal_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_stock_removal(removal_id: UUID,
                         db: db_dependency,
                         current_user: Annotated[dict, Depends(require_access_level(3))]):
    try:
        stock_removal = db.query(StockRemoval).filter(
            StockRemoval.id == removal_id).first()
        if not stock_removal:
            raise HTTPException(
                status_code=404, detail="Stock Removal not found.")

        products = {
            p.product_id: p.removal_quantity for p in stock_removal.items}
        restore_inventory(db, products, add_stock=True)

        db.delete(stock_removal)
        db.commit()
        return

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Error Occurred While Deleting the Stock Removal Application")

# P.S: Deletion of Stock Removal is highly discouraged, instead Use the Update API to Cancel the operation.
# Also, Once Removed Application is submitted the Items Cannot be Changed.
