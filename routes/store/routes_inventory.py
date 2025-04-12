from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from validations.inventory import (
    InventoryResponse,
    InventoryResponseWithProduct,
    InventoryRequest,
    InventoryUpdateRequest
)
from utils.db import db_dependency
from schemas.inventory import Inventory
from uuid import UUID
from utils.auth import require_access_level


router = APIRouter(prefix="/inventory")


@router.get("/all",
            response_model=List[InventoryResponse],
            status_code=status.HTTP_200_OK)
async def get_all_inventory(db: db_dependency,
                            product_details: bool = False,
                            offset: int = 0,
                            limit: int = 100):
    """Retrieve all Inventory."""
    try:
        complete_inventory = (
            db.query(Inventory)
            .offset(offset)
            .limit(limit)
            .all()
        )
        if product_details:
            return [InventoryResponseWithProduct.model_validate(inventory)
                    for inventory in complete_inventory]

        return [InventoryResponse.model_validate(inventory) for inventory in complete_inventory]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Records: {str(e)}")


@router.get("/get/{store_id}",
            response_model=List[InventoryResponse],
            status_code=status.HTTP_200_OK)
async def get_inventory_by_store(store_id: UUID, db: db_dependency,
                                 product_details: bool = False,
                                 offset: int = 0,
                                 limit: int = 100):
    """Retrieve Inventory for a specific Store."""
    try:
        complete_inventory = (
            db.query(Inventory)
            .filter(Inventory.store_id == store_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        if not complete_inventory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Inventory Not Found.")

        if product_details:
            return [InventoryResponseWithProduct.model_validate(inventory)
                    for inventory in complete_inventory]

        return [InventoryResponse.model_validate(inventory) for inventory in complete_inventory]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Records: {str(e)}")


@router.post("/add",
             response_model=InventoryResponse,
             status_code=status.HTTP_201_CREATED)
async def add_inventory(inventory: InventoryRequest, db: db_dependency,
                        current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Add a new Inventory Record."""
    try:
        if not inventory:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Inventory Data Provided")

        new_inventory = Inventory(**inventory.model_dump())
        db.add(new_inventory)
        db.commit()

        db.refresh(new_inventory)
        return InventoryResponse.model_validate(new_inventory)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Adding Record: {str(e)}")


@router.put("/mod/{store_id}",
            response_model=List[InventoryResponse],
            status_code=status.HTTP_202_ACCEPTED)
async def modify_inventory(store_id: UUID,
                           update_data: List[InventoryUpdateRequest],
                           db: db_dependency,
                           current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Update Inventory for a Specific Store."""
    try:
        inventory_records = db.query(Inventory).filter(
            Inventory.store_id == store_id).all()

        if not inventory_records:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Inventory Not Found")

        if not update_data:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Updated Inventory Provided")

        inventory_map = {
            record.product_id: record for record in inventory_records}
        updated_items = []

        for update in update_data:
            inventory = inventory_map.get(update.product_id)

            if not inventory:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Inventory Not Found for Product ID: {update.product_id}")

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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Records: {str(e)}")


@router.delete("/del/{store_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_by_store(store_id: UUID,
                                    product_ids: List[UUID],
                                    db: db_dependency,
                                    current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Delete Inventory Products for a specific Store. Usage is Highly Discouraged.
        Removal End-Points should be used to perform Inventory Removals.
    """
    try:
        (db.query(Inventory)
         .filter(Inventory.store_id == store_id, Inventory.product_id.in_(product_ids))
         .delete(synchronize_session="fetch"))
        db.commit()

        return

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Deleting Records: {str(e)}")


# Note: Direct modifications to inventory via this API are discouraged.
# Please use Stock Removal or Restock APIs to ensure proper auditing.
