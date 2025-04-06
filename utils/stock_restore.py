from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.inventory import Inventory
from uuid import UUID


def restore_inventory(db: Session, products: dict[UUID, int], add_stock: bool):
    """
    Restores inventory quantities based on the items from a stock removal operation.
    This is typically used when a stock removal is cancelled or deleted.
    """
    inventories = {
        inv.product_id: inv
        for inv in db.query(Inventory).filter(
            Inventory.product_id.in_(products)
        ).all()
    }

    for product_id, quantity in products.items():
        inventory = inventories.get(product_id)
        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"Product {product_id} not found in inventory.")
            
        if add_stock:
            inventory.quantity += quantity
        
        else:
            inventory.quantity = max(0, inventory.quantity - quantity)
            
