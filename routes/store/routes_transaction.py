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
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.date.desc())
            .all()
        )

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
        transaction = (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )
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
        query = db.query(Transaction)

        if store_id:
            query = query.filter(Transaction.store_id == store_id)
        if operation_type:
            query = query.filter(Transaction.operation_type == operation_type)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = (
            query.order_by(Transaction.date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            TransactionResponseWithRelations.model_validate(transaction)
            for transaction in transactions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Fetching Filtered Transactions: {str(e)}"
        )
