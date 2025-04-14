from schemas.employee import Employee
from schemas.order import Order
from schemas.refund import Refund
from schemas.inventory import Inventory
from schemas.removal import StockRemoval
from schemas.restock import Restock
from schemas.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from validations.store import StoreResponseWithRelations, StoreWithIncludeRelationsRequest


async def load_store_related_data(store_model: StoreResponseWithRelations,
                                  db: AsyncSession,
                                  config: StoreWithIncludeRelationsRequest):
    
    if config.inlcude_inventory:
        stmt = (
            select(Inventory)
            .where(Inventory.store_id == config.id)
            .offset(config.inventory_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.inventory = result.scalars().all()

    if config.include_employee:
        stmt = (
            select(Employee)
            .where(Employee.store_id == config.id)
            .offset(config.employee_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.employees = result.scalars().all()

    if config.include_transactions:
        stmt = (
            select(Transaction)
            .where(Transaction.store_id == config.id)
            .order_by(Transaction.date.desc())
            .offset(config.transactions_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.transactions = result.scalars().all()

    if config.include_restock:
        stmt = (
            select(Restock)
            .where(Restock.store_id == config.id)
            .order_by(Restock.date.desc())
            .offset(config.restock_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.restocks = result.scalars().all()

    if config.include_removal:
        stmt = (
            select(StockRemoval)
            .where(StockRemoval.store_id == config.id)
            .order_by(StockRemoval.date.desc())
            .offset(config.removal_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.removals = result.scalars().all()

    if config.include_order:
        stmt = (
            select(Order)
            .where(Order.store_id == config.id)
            .order_by(Order.date_placed.desc())
            .offset(config.order_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.orders = result.scalars().all()

    if config.include_refund:
        stmt = (
            select(Refund)
            .where(Refund.store_id == config.id)
            .order_by(Refund.date.desc())
            .offset(config.refund_offset)
            .limit(config.records_limit)
        )
        result = await db.execute(stmt)
        store_model.refunds = result.scalars().all()

    return store_model