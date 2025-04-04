from fastapi import HTTPException
from schemas.order import CartItems
from validations.order import CartItemBase
from typing import List

def create_cart_items(order_items: List[CartItemBase | CartItems], products: dict, tax_rate: int=0.18):
    total_amount = 0
    total_discount = 0
    total_tax = 0
    cart_items = []
    for item in order_items:
        if item.product_id not in products:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        product = products[item.product_id]
        item_price = product.price * item.quantity
        item_discount = item_price * item.discount
        item_tax = (item_price - item_discount) * tax_rate

        total_amount += item_price
        total_discount += item_discount
        total_tax += item_tax

        cart_items.append(CartItems(
            product_id=item.product_id,
            quantity=item.quantity,
            discount=item.discount
        ))
        
    return cart_items, total_amount, total_discount, total_tax