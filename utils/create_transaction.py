from schemas.transaction import Transaction
from validations.store import TransactionBase
from uuid import UUID
from schemas.order import Order
from schemas.refund import Refund
from schemas.restock import Restock
from schemas.removal import StockRemoval
from utils.db import db_dependency


def add_transaction(record, handler_id: UUID, db: db_dependency):
    if isinstance(record, Order):
        op_type = "Sale"
        
    elif isinstance(record, Refund):
        op_type = "Refund"
        
    elif isinstance(record, Restock):
        op_type = "Restock"
        
    elif isinstance(record, StockRemoval):
        op_type = "Removal"
    
    else:
        raise ValueError(f"Invalid Record type. Expected StockRemoval, Order, Refund or Restock, got: {type(record)}")
    
    validation_model = TransactionBase(type=op_type,
                                       operation_id=record.id,
                                       handler_id=handler_id)
    
    transaction = Transaction(**validation_model.model_dump())
    db.add(transaction)
    
    
    
