from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from uuid import UUID
from schemas.store import Store
from validations.store import (
    StoreRequest,
    StoreResponse,
    StoreResponseWithRelations,
    StoreUpdateRequest,
    StoreWithIncludeRelationsRequest
)
from utils.db import db_dependency
from utils.auth import require_access_level
from utils.information_loader import load_store_related_data


router = APIRouter(prefix="/stores")


@router.post("/add",
             response_model=List[StoreResponse],
             status_code=status.HTTP_201_CREATED)
async def create_stores(stores: List[StoreRequest],
                        db: db_dependency,
                        current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Create New Stores."""
    try:
        new_stores = [Store(**store.model_dump()) for store in stores]
        db.add_all(new_stores)
        db.commit()
        return [StoreResponse.model_validate(store) for store in new_stores]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Creating Stores: {str(e)}")


@router.get("/all",
            response_model=List[StoreResponse],
            status_code=status.HTTP_200_OK)
async def get_all_stores(db: db_dependency):
    """Retrieve All Registered Stores."""
    try:
        stores = db.query(Store).all()
        return [StoreResponse.model_validate(store) for store in stores]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Stores: {str(e)}")


@router.post("/get/{store_id}",
             response_model=StoreResponseWithRelations,
             status_code=status.HTTP_200_OK)
async def get_store_by_id(store_response_config: StoreWithIncludeRelationsRequest,
                          db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(2))],
                          ):
    """Retrieve a Store and its Related Information by ID."""
    try:
        store = (
            db.query(Store)
            .filter(Store.id == store_response_config.id)
            .first()
        )
        location = store.location
        store_model = StoreResponseWithRelations(**store.__dict__)
        store_model.location = location
        store_model = load_store_related_data(
            store_model, db, store_response_config)
        return store_model

    except HTTPException as e:
        raise e

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
