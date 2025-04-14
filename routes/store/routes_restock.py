from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated, Optional
from uuid import UUID
from datetime import date
from utils.db import db_dependency
from validations.restock import RestockRequest, RestockResponse, RestockUpdateRequest
from schemas.restock import Restock
from utils.stock_restore import restore_inventory
from utils.auth import require_access_level
from utils.create_transaction import add_transaction
from utils.restock_creator import create_restock_items, add_restock_items_to_inventory
from sqlalchemy.future import select

router = APIRouter(prefix="/restocks")


@router.post("/add",
             response_model=RestockResponse,
             status_code=status.HTTP_201_CREATED)
async def create_restock(restock_data: RestockRequest,
                   db: db_dependency,
                   current_user: Annotated[dict, Depends(require_access_level(3))]):
    try:

        restock_items = create_restock_items(restock_data, db)
        new_restock = Restock(
            store_id=restock_data.store_id,
            status=restock_data.status,
            date_placed=restock_data.date_placed,
            date_received=restock_data.date_received,
            items=restock_items)

        await add_transaction(new_restock, current_user["id"], db)
        await db.add(new_restock)
        await db.commit()
        await db.refresh(new_restock)
        return RestockResponse.model_validate(new_restock)


    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Internal Server Error: {str(e)}")


@router.get("/get/{restock_id}",
            response_model=RestockResponse,
            status_code=status.HTTP_200_OK)
async def get_restock(restock_id: UUID,
                db: db_dependency,
                current_user: Annotated[dict, Depends(require_access_level(2))]):
    try:
        stmt = select(Restock).where(Restock.id == restock_id)
        result = await db.execute(stmt)
        restock = result.scalar_one_or_none()
        if not restock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Restock Order Not Found")
        return RestockResponse.model_validate(restock)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Restock Record: {str(e)}")


@router.get("/filter",
            response_model=List[RestockResponse],
            status_code=status.HTTP_200_OK)
async def get_filtered_restocks(db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(2))],
                          store_id: Optional[UUID] = None,
                          status: Optional[str] = None,
                          date_placed: Optional[date] = None,
                          date_received: Optional[date] = None,
                          limit: int = 50,
                          offset: int = 0):
    try:
        stmt = select(Restock)

        if store_id:
            stmt = stmt.where(Restock.store_id == store_id)
            
        if status:
            stmt = stmt.where(Restock.status.ilike(status))
            
        if date_placed:
            stmt = stmt.where(Restock.date_placed == date_placed)
            
        if date_received:
            stmt = stmt.where(Restock.date_received == date_received)
        
        result = await db.execute(stmt)
        restocks = result.scalars().all()
        return [RestockResponse.model_validate(r) for r in restocks]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Restock Records: {str(e)}")


@router.get("/all",
            response_model=List[RestockResponse],
            status_code=status.HTTP_200_OK)
async def get_restocks(db: db_dependency,
                 current_user: Annotated[dict, Depends(require_access_level(2))],
                 limit: int = 10,
                 offset: int = 0):
    try:
        stmt = select(Restock).offset(offset).limit(limit)
        result = await db.execute(stmt)
        restocks = result.scalars().all()
        return [RestockResponse.model_validate(r) for r in restocks]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Restock Records: {str(e)}")


@router.put("/mod/{restock_id}",
            response_model=RestockResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_restock(restock_id: UUID,
                   new_data: RestockUpdateRequest,
                   db: db_dependency,
                   current_user: Annotated[dict, Depends(require_access_level(2))]):
    try:
        stmt = select(Restock).where(Restock.id == restock_id)
        result = await db.execute(stmt)
        restock = result.scalar_one_or_none()

        if not restock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Restock Order Not Found")

        if new_data.status is not None:
            restock.status = new_data.status
        if new_data.date_received is not None:
            restock.date_received = new_data.date_received

        if new_data.status == "Cancelled":
            products = {p.id: p.restock_quantity for p in restock.items}
            await restore_inventory(db, products, add_stock=False)

        elif new_data.status == "Completed":
            await add_restock_items_to_inventory(restock, db)

        await db.commit()
        await db.refresh(restock)
        return RestockResponse.model_validate(restock)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error Updating Restock: {str(e)}")


@router.delete("/del/{restock_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_restock(restock_id: UUID,
                   db: db_dependency,
                   current_user: Annotated[dict, Depends(require_access_level(4))]):
    try:
        stmt = select(Restock).where(Restock.id == restock_id)
        result = await db.execute(stmt)
        restock = result.scalar_one_or_none()()
        if not restock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Restock Record Not Found")

        products = {p.id: p.restock_quantity for p in restock.items}
        await restore_inventory(db, products, add_stock=False)

        await db.delete(restock)
        await db.commit()
        return

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Deleting Restock: {str(e)}")
