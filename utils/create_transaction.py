from schemas.transaction import Transaction
from validations.transaction import TransactionBase
from uuid import UUID
from schemas.order import Order
from schemas.refund import Refund
from schemas.restock import Restock
from schemas.removal import StockRemoval
from sqlalchemy.orm import Session


def add_transaction(record, request_made_by: UUID, db: Session):
    if isinstance(record, Order):
        op_type = "Sale"

    elif isinstance(record, Refund):
        op_type = "Refund"

    elif isinstance(record, Restock):
        op_type = "Restock"

    elif isinstance(record, StockRemoval):
        op_type = "Removal"

    else:
        raise ValueError(
            f"Invalid Record type. Expected StockRemoval, Order, Refund or Restock, got: {type(record)}")

    validation_model = TransactionBase(type=op_type,
                                       operation_id=record.id,
                                       request_made_by=request_made_by)

    transaction = Transaction(**validation_model.model_dump())
    db.add(transaction)
