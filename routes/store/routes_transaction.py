from fastapi import APIRouter, HTTPException
from typing import List
from schemas.transaction import Transaction
from validations.store import TransactionResponseWithRelations, TransactionResponse
from utils.db import db_dependency
from uuid import UUID


router = APIRouter(prefix="/transactions")

# P.S: No Routes for Transaction Creation and Modification will be Exposed, Only Retrievals are allowed.

@router.get("/all", response_model=List[TransactionResponseWithRelations])
async def get_all_transactions(db: db_dependency, include_details=False):
    """Retrieve all Transactions."""
    try:
        transactions = db.query(Transaction).order_by(Transaction.date.desc()).all()
        
        if include_details:
            return [TransactionResponseWithRelations.model_validate(transaction) for transaction in transactions]
        
        return [TransactionResponse.model_validate(transaction) for transaction in transactions]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Transactions: {str(e)}")
    

@router.get("/get/{transaction_id}", response_model=TransactionResponseWithRelations)
async def get_transaction(transaction_id: UUID, db: db_dependency):
    """Retrieve a Transaction by ID."""
    try:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction Not Found")  
        return TransactionResponseWithRelations.model_validate(transaction)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Transaction: {str(e)}")


@router.get("/all/store/{store_id}", response_model=List[TransactionResponseWithRelations])
async def get_transactions_by_store(store_id: UUID, db: db_dependency, limit:int=50, offset:int=0):
    """Retrieve a Transaction by ID."""
    try:
        transactions = (
            db.query(Transaction)
            .filter(Transaction.store_id == store_id)
            .order_by(Transaction.date.desc())
            .offset(offset)
            .limit(limit)
            .all())
        
        return [TransactionResponseWithRelations.model_validate(transaction) for transaction in transactions]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Transactions: {str(e)}")