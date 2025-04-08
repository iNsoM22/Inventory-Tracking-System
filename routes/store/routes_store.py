from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from schemas.store import Store
from validations.store import (
    StoreRequest,
    StoreResponse,
    StoreResponseWithRelations,
    StoreUpdateRequest
)
from utils.db import db_dependency


router = APIRouter(prefix="/stores")


@router.post("/add",
             response_model=List[StoreResponse],
             status_code=status.HTTP_201_CREATED)
async def create_stores(stores: List[StoreRequest], db: db_dependency):
    """Create New Stores."""
    try:
        new_stores = [Store(**store.model_dump()) for store in stores]
        db.add_all(new_stores)
        db.commit()
        return [StoreResponse.model_validate(store) for store in new_stores]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Creating Stores: {str(e)}")


@router.get("/all",
            response_model=List[StoreResponse],
            status_code=status.HTTP_200_OK)
async def get_all_stores(db: db_dependency):
    """Retrieve All Registered Stores."""
    try:
        stores = db.query(Store).all()
        return [StoreResponse.model_validate(store) for store in stores]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Stores: {str(e)}")


@router.get("/get/{store_id}",
            response_model=StoreResponseWithRelations,
            status_code=status.HTTP_200_OK)
async def get_store_by_id(store_id: UUID,
                          db: db_dependency,
                          include_employees: bool = False,
                          include_inventory: bool = False,
                          include_transactions: bool = False,
                          include_restocks: bool = False,
                          include_removals: bool = False,
                          include_orders: bool = False,
                          include_refunds: bool = False):
    """Retrieve a Store and its Related Information by ID."""
    try:
        store = (
            db.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

        return StoreResponseWithRelations.include_related_information(
            store,
            include_employees=include_employees,
            include_inventories=include_inventory,
            include_transactions=include_transactions,
            include_restocks=include_restocks,
            include_removals=include_removals,
            include_orders=include_orders,
            include_refunds=include_refunds
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Store: {str(e)}")


@router.put("/update/{store_id}",
            response_model=StoreResponse,
            status_code=status.HTTP_200_OK)
async def update_store(store_id: UUID, store: StoreUpdateRequest, db: db_dependency):
    """Update a Store's Details."""
    try:
        store_to_update = (
            db.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

        if not store_to_update:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Store Not Found")

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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Store: {str(e)}")


@router.delete("/del/{store_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_store(store_id: UUID, db: db_dependency):
    """Delete a Store by ID."""
    try:
        store = (
            db.query(Store)
            .filter(Store.id == store_id)
            .first()
        )
        if not store:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Store Not Found")

        db.delete(store)
        db.commit()

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Deleting Store: {str(e)}")
