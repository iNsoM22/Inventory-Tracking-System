from uuid import UUID
from schemas.order import Order
from schemas.inventory import Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.refund import Refund
from schemas.transaction import Transaction
from sqlalchemy.future import select


async def check_and_remove_inventory(order: Order,
                               store_id: UUID,
                               db: AsyncSession):
    products = {p.product_id: p for p in order.items}
    stmt = select(Inventory).where(Inventory.product_id.in_(products), Inventory.store_id == store_id)
    results = await db.execute(stmt)
    inventories = results.scalars().all()
    for inventory in inventories:
        product = products[inventory.product_id]
        if inventory.quantity < product.quantity:
            raise ValueError(f"Not enough inventory for Product {product.id} in Store {store_id}.\
                                        Only {inventory.quantity} Available.")

        inventory.quantity -= product.quantity


async def check_and_add_inventory(order, operation_type: str, db: AsyncSession):
    stmt = select(Transaction).where(Transaction.type == operation_type)
    
    if isinstance(order, Order):
        stmt = stmt.where(Transaction.operation_id == order.id)
        result = await db.execute(stmt)
        transaction = result.scalars().first()
        
    elif isinstance(order, Refund):
        stmt = stmt.where(Transaction.operation_id == order.order_id)
        result = await db.execute(stmt)
        transaction = result.scalars().first()

    products = {p.product_id: p for p in order.items}
    stmt = select(Inventory).where(Inventory.product_id.in_(products), Inventory.store_id == order.store_id)
    results = await db.execute(stmt)
    inventories = results.scalars().all()
    
    for inventory in inventories:
        product = products[inventory.product_id]
        inventory.quantity += product.quantity
