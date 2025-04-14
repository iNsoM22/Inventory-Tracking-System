from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated, Optional
from uuid import UUID
from schemas.transaction import Transaction
from validations.transaction import (
    TransactionResponseWithRelations,
    TransactionResponse
)
from datetime import date
from utils.db import db_dependency
from utils.auth import require_access_level
from sqlalchemy.future import select

router = APIRouter(prefix="/transactions")

# NOTE: No Routes for Transaction Creation and Modification will be Exposed. Only Retrievals are Allowed.


@router.get("/all",
            response_model=List[TransactionResponseWithRelations],
            status_code=status.HTTP_200_OK)
async def get_all_transactions(db: db_dependency,
                               current_user: Annotated[dict, Depends(require_access_level(3))],
                               include_details: bool = False):
    """Retrieve all Transactions."""
    try:
        stmt = select(Transaction).order_by(Transaction.date.desc())
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        if include_details:
            return [
                TransactionResponseWithRelations.model_validate(transaction)
                for transaction in transactions
            ]

        return [
            TransactionResponse.model_validate(transaction)
            for transaction in transactions
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Transactions: {str(e)}")


@router.get("/get/{transaction_id}",
            response_model=TransactionResponseWithRelations,
            status_code=status.HTTP_200_OK)
async def get_transaction(transaction_id: UUID,
                          db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Retrieve a Transaction by ID."""
    try:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await db.execute(stmt)
        transaction = result.scalars().first()
        
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Transaction Not Found")

        return TransactionResponseWithRelations.model_validate(transaction)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Transaction: {str(e)}")


@router.get("/filter",
            response_model=List[TransactionResponseWithRelations],
            status_code=status.HTTP_200_OK)
async def filter_transactions(db: db_dependency,
                              current_user: Annotated[dict, Depends(require_access_level(3))],
                              store_id: Optional[UUID] = None,
                              operation_type: Optional[str] = None,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              limit: int = 50,
                              offset: int = 0):
    try:
        stmt = select(Transaction)

        if store_id:
            stmt = stmt.where(Transaction.store_id == store_id)
        if operation_type:
            stmt = stmt.where(Transaction.operation_type == operation_type)
        if start_date:
            stmt = stmt.where(Transaction.date >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.date <= end_date)

        stmt = stmt.order_by(Transaction.date.desc()).offset(offset).limit(limit)
        result = await db.execute(stmt)
        transactions = result.scalars().all()

        return [
            TransactionResponseWithRelations.model_validate(transaction)
            for transaction in transactions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Fetching Filtered Transactions: {str(e)}"
        )
