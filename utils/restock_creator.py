from schemas.restock import RestockItems, Restock
from validations.restock import RestockRequest
from schemas.inventory import Inventory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_restock_items(restock_data: RestockRequest, db: AsyncSession):
    products = {p.product_id: p for p in restock_data.items}
    
    result = await db.execute(
        select(Inventory)
        .filter(Inventory.store_id == restock_data.store_id, Inventory.product_id.in_(products))
    )
    store_inventory = {p.product_id: p for p in result.scalars().all()}
    
    restock_items = []
    for item in restock_data.items:
        product_from_store_inventory = store_inventory.get(item.product_id, None)

        previous_quantity = product_from_store_inventory.quantity if product_from_store_inventory else 0

        restock_item = RestockItems(
            product_id=item.product_id,
            previous_quantity=previous_quantity,
            restock_quantity=item.restock_quantity)

        restock_items.append(restock_item)

    return restock_items



async def add_restock_items_to_inventory(restock: Restock, db: AsyncSession):
    restock_items = {p.product_id: p for p in restock.items}
    
    result = await db.execute(
        select(Inventory)
        .filter(Inventory.store_id == restock.store_id, Inventory.product_id.in_(restock_items))
    )
    
    store_inventory = {p.product_id: p for p in result.scalars().all()}
    
    new_inventory_records = []
    for item_id, item in restock_items.items():
        product_from_store_inventory = store_inventory.get(item_id, None)
        if product_from_store_inventory:
            product_from_store_inventory.quantity += item.restock_quantity
        else:
            new_item = Inventory(
                store_id=restock.store_id,
                product_id=item.product_id,
                quantity=item.restock_quantity,
                max_discount_amount=0
            )
            new_inventory_records.append(new_item)
            await db.add(new_item)
