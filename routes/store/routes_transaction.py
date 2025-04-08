from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID

from schemas.transaction import Transaction
from validations.transaction import (
    TransactionResponseWithRelations,
    TransactionResponse
)
from utils.db import db_dependency


router = APIRouter(prefix="/transactions")

# NOTE: No Routes for Transaction Creation and Modification will be Exposed. Only Retrievals are Allowed.


@router.get("/all",
            response_model=List[TransactionResponseWithRelations],
            status_code=status.HTTP_200_OK)
async def get_all_transactions(db: db_dependency, include_details: bool = False):
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
async def get_transaction(transaction_id: UUID, db: db_dependency):
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


@router.get("/all/store/{store_id}",
            response_model=List[TransactionResponseWithRelations],
            status_code=status.HTTP_200_OK)
async def get_transactions_by_store(store_id: UUID, db: db_dependency,
                                    limit: int = 50, offset: int = 0):
    """Retrieve all Transactions for a Specific Store."""
    try:
        transactions = (
            db.query(Transaction)
            .filter(Transaction.store_id == store_id)
            .order_by(Transaction.date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            TransactionResponseWithRelations.model_validate(transaction)
            for transaction in transactions
        ]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Transactions: {str(e)}")
