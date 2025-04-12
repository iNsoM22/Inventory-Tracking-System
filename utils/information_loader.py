from schemas.employee import Employee
from schemas.order import Order
from schemas.refund import Refund
from schemas.inventory import Inventory
from schemas.removal import StockRemoval
from schemas.restock import Restock
from schemas.transaction import Transaction
from sqlalchemy.orm import Session
from validations.store import StoreResponseWithRelations, StoreWithIncludeRelationsRequest


def load_store_related_data(
    store_model: StoreResponseWithRelations,
    db: Session,
    config: StoreWithIncludeRelationsRequest
):
    if config.inlcude_inventory:
        store_model.inventory = (
            db.query(Inventory)
            .filter(Inventory.store_id == config.id)
            .offset(config.inventory_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_employee:
        store_model.employees = (
            db.query(Employee)
            .filter(Employee.store_id == config.id)
            .offset(config.employee_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_transactions:
        store_model.transactions = (
            db.query(Transaction)
            .filter(Transaction.store_id == config.id)
            .order_by(Transaction.date.desc())
            .offset(config.transactions_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_restock:
        store_model.restocks = (
            db.query(Restock)
            .filter(Restock.store_id == config.id)
            .order_by(Restock.date.desc())
            .offset(config.restock_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_removal:
        store_model.removals = (
            db.query(StockRemoval)
            .filter(StockRemoval.store_id == config.id)
            .order_by(StockRemoval.date.desc())
            .offset(config.removal_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_order:
        store_model.orders = (
            db.query(Order)
            .filter(Order.store_id == config.id)
            .order_by(Order.date_placed.desc())
            .offset(config.order_offset)
            .limit(config.records_limit)
            .all()
        )

    if config.include_refund:
        store_model.refunds = (
            db.query(Refund)
            .filter(Refund.store_id == config.id)
            .order_by(Refund.date.desc())
            .offset(config.refund_offset)
            .limit(config.records_limit)
            .all()
        )

    return store_model
