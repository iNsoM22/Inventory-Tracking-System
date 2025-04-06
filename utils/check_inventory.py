from uuid import UUID
from schemas.order import Order
from schemas.inventory import Inventory
from utils.db import db_dependency
from schemas.refund import Refund
from schemas.transaction import Transaction


def check_and_remove_inventory(order: Order, store_id: UUID,  db: db_dependency):
    products = {p.product_id: p for p in order.items}
    inventories = db.query(Inventory).filter(Inventory.product_id.in_(products), Inventory.store_id == store_id).all()
    for inventory in inventories:
        product = products[inventory.product_id]
        if inventory.quantity < product.quantity:
            raise ValueError(f"Not enough inventory for Product {product.id} in Store {store_id}. Only {inventory.quantity} Available.")
        
        inventory.quantity -= product.quantity
            
    
    
    
def check_and_add_inventory(order, operation_type: str, db: db_dependency):
    if isinstance(order, Order):
        transaction = db.query(Transaction).filter(Transaction.operation_id == order.id, Transaction.type == operation_type).first()
    elif isinstance(order, Refund):
        transaction = db.query(Transaction).filter(Transaction.operation_id == order.order_id, Transaction.type == operation_type).first()
    
    products = {p.product_id: p for p in order.items}
    inventories = db.query(Inventory).filter(Inventory.product_id.in_(products), Inventory.store_id == transaction.store_id).all()
    for inventory in inventories:
        product = products[inventory.product_id]
        inventory.quantity += product.quantity
    