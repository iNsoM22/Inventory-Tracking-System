from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.inventory import Inventory
from uuid import UUID


def restore_inventory(db: Session, store_id: UUID,
                      products: dict[UUID, int], add_stock: bool):
    """
    Restores inventory quantities based on the items from a stock removal operation.
    This is typically used when a stock removal is cancelled or deleted.
    """
    inventories = {
        inv.product_id: inv
        for inv in (
            db.query(Inventory)
            .filter(Inventory.product_id.in_(products), Inventory.store_id == store_id)
            .all()
        )
    }

    for product_id, quantity in products.items():
        inventory = inventories.get(product_id)
        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} Not Found in Inventory.")

        if add_stock:
            inventory.quantity += quantity

        elif inventory.quantity >= quantity:
            inventory.quantity = inventory.quantity - quantity

        else:
            raise ValueError(f"Not enough inventory for Product {product_id} in Store {store_id}.\
                                Only {inventory.quantity} Available.")
