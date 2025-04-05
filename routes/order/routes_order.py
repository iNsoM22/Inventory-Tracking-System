from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from datetime import datetime, timezone
from utils.db import db_dependency
from utils.cart_creator import create_cart_items
from schemas.order import Order
from schemas.product import Product 
from schemas.customer import Customer
from validations.order import OrderRequest, OrderResponse, OrderUpdateRequest, CartItemUpdateRequest


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/add", response_model=OrderResponse)
def create_order(order_data: OrderRequest, db: db_dependency):
    customer = db.query(Customer).filter(Customer.id == order_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer Not Found")

    product_ids = [item.product_id for item in order_data.items]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()}

    cart_items, total_amount, total_discount, total_tax = create_cart_items(order_data.items, products)

    new_order = Order(
        customer_id=order_data.customer_id,
        order_amount=total_amount,
        discount_amount=total_discount,
        tax=total_tax,
        status=order_data.status,
        date_placed=datetime.now(timezone.utc),
        order_mode=order_data.order_mode,
        items=cart_items
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return OrderResponse.model_validate(new_order)


@router.get("/get/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, db: db_dependency):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")
        return OrderResponse.model_validate(order)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Order: {str(e)}")
    
    
@router.get("/all", response_model=List[OrderResponse])
async def get_orders(limit: int, offset: int, db: db_dependency):
    try:
        def_offset = 0 if not offset else offset
        def_limit = 10 if not limit else limit
        orders = db.query(Order).offset(def_offset).limit(def_limit).all()
        return [OrderResponse.model_validate(order) for order in orders]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Orders: {str(e)}")
    
    

@router.put("/mod/{order_id}", response_model=OrderResponse)
def update_order(order_id: UUID, new_order_data: OrderUpdateRequest, db: db_dependency):
    """Status Update for the Order."""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")
        
        order.status = new_order_data.status
        order.date_received = new_order_data.date_received
        
        db.commit()
        db.refresh(order)
        return OrderResponse.model_validate(order)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Order: {str(e)}")
    
    
@router.delete("/del/{order_id}", status_code=204)
async def delete_order(order_id: UUID, db: db_dependency):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
    
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")

        db.delete(order)
        db.commit()
        return {"detail": "Order and Related Cart Items have been deleted successfully."}
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Order: {str(e)}")
    


@router.put("/mod/cart/{order_id}", response_model=OrderResponse)
def update_cart_items(order_id: UUID, items_update_request: List[CartItemUpdateRequest], db: db_dependency):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")
        
        cart_items_dict = {(item.product_id): item for item in order.items}

        for item_update in items_update_request:
            cart_item = cart_items_dict.get(item_update.product_id)
            if not cart_item:
                raise HTTPException(status_code=404, detail=f"Product {item_update.product_id} Not Found in the Order.")
            
            if item_update.quantity == 0:
                del cart_items_dict[item_update.product_id]
                db.delete(cart_item)
                continue

            if item_update.quantity is not None:
                cart_item.quantity = item_update.quantity

            if item_update.discount is not None:
                cart_item.discount = item_update.discount
            
        products = {p.id: p for p in db.query(Product).filter(Product.id.in_(cart_items_dict)).all()}
        cart_items, total_amount, total_discount, total_tax = create_cart_items(cart_items_dict.values(), products)
        
        order.order_amount = total_amount
        order.discount_amount = total_discount
        order.tax = total_tax
        order.items = cart_items
        
        db.commit()
        db.refresh(order)
        
        return OrderResponse.model_validate(order)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Cart Items: {str(e)}")
                
            
                
# P.S: Order Cart Items Update End-Points are exposed but their usage is highly discouraged.
# Once the Order is created, Items should not be Updated. 
# For this, Cancel the Previous Order and Create a New One with Correct Information.