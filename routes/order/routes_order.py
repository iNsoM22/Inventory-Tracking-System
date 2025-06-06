from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from uuid import UUID
from datetime import datetime, timezone
from utils.db import db_dependency
from utils.cart_creator import create_cart_items
from schemas.order import Order
from schemas.product import Product
from schemas.customer import Customer
from validations.order import OrderRequest, OrderResponse, OrderUpdateRequest, CartItemUpdateRequest
from utils.check_inventory import check_and_remove_inventory, check_and_add_inventory
from utils.auth import require_access_level, user_dependency
from utils.create_transaction import add_transaction
from sqlalchemy.future import select


router = APIRouter(prefix="/orders")


@router.post("/add",
             response_model=OrderResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderRequest,
                 db: db_dependency,
                 current_user: user_dependency):
    try:
        stmt = select(Customer).where(Customer.id == order_data.customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Cannot Perform Order with Differring ID and Token")

        if not order_data.items:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="Cannot Place Order with an Empty Cart")

        product_ids = [item.product_id for item in order_data.items]
        stmt = select(Product).where(Product.id.in_(product_ids))
        result = await db.execute(stmt)
        products = {p.id: p for p in result.scalars().all()}

        cart_items, total_amount, total_discount, total_tax = create_cart_items(
            order_data.items, products)

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
        await check_and_remove_inventory(new_order, order_data.store_id, db)
        add_transaction(new_order, current_user["id"], db)
        await db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return OrderResponse.model_validate(new_order)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error Fetching Order: {str(e)}")


@router.get("/get/{order_id}",
            response_model=OrderResponse,
            status_code=status.HTTP_200_OK)
async def get_order(order_id: UUID, db: db_dependency,
              current_user: user_dependency):
    try:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order Not Found")
        return OrderResponse.model_validate(order)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Order: {str(e)}")


@router.get("/all",
            response_model=List[OrderResponse],
            status_code=status.HTTP_200_OK)
async def get_orders(db: db_dependency,
                     current_user: Annotated[dict, Depends(require_access_level(2))],
                     limit: int = 50,
                     offset: int = 0):
    try:
        stmt = select(Order).offset(offset).limit(limit)
        result = await db.execute(stmt)
        orders = result.scalars().all()
        return [OrderResponse.model_validate(order) for order in orders]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Orders: {str(e)}")


@router.put("/mod/{order_id}",
            response_model=OrderResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_order(order_id: UUID, new_order_data: OrderUpdateRequest,
                 db: db_dependency, current_user: user_dependency):
    """Status Update for the Order."""
    try:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")

        if current_user["id"] != order.customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Cannot Perform Order with Differring IDs, Unless Not an internal User.")

        order.status = new_order_data.status
        order.date_received = new_order_data.date_received

        if new_order_data.status == "Cancelled":
            await check_and_add_inventory(order, operation_type="Sale", db=db)

        await db.commit()
        await db.refresh(order)
        return OrderResponse.model_validate(order)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Order: {str(e)}")


@router.delete("/del/{order_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: UUID, db: db_dependency,
                       current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Delete an Order. This End-Point Should be Used Carefully, 
    Otherwise it will result in discrepencies."""
    try:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")

        await check_and_add_inventory(order, operation_type="Sale", db=db)
        await db.delete(order)
        await db.commit()
        return

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error Deleting Order: {str(e)}")


@router.put("/mod/cart/{order_id}",
            response_model=OrderResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_cart_items(order_id: UUID,
                      items_update_request: List[CartItemUpdateRequest],
                      db: db_dependency,
                      current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Update Cart Items of an Order, Usage is highly Discouraged."""
    try:
        stmt = select(Order).where(Order.id == order_id)
        result = await db.execute(stmt)
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Order Not Found")

        cart_items_dict = {(item.product_id): item for item in order.items}

        for item_update in items_update_request:
            cart_item = cart_items_dict.get(item_update.product_id)
            if not cart_item:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Product {item_update.product_id} Not Found in the Order.")

            if item_update.quantity == 0:
                del cart_items_dict[item_update.product_id]
                await db.delete(cart_item)
                continue

            if item_update.quantity is not None:
                cart_item.quantity = item_update.quantity

            if item_update.discount is not None:
                cart_item.discount = item_update.discount
        
        stmt = select(Product.id, Product.price, Product.discount).where(Product.id.in_(cart_items_dict))
        results = await db.execute(stmt)
        products = {p.id: p for p in results}
        cart_items, total_amount, total_discount, total_tax = create_cart_items(
            cart_items_dict.values(), products)

        order.order_amount = total_amount
        order.discount_amount = total_discount
        order.tax = total_tax
        order.items = cart_items

        await db.commit()
        await db.refresh(order)

        return OrderResponse.model_validate(order)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Cart Items: {str(e)}")


# P.S: Order Cart Items Update End-Points are exposed but their usage is highly discouraged.
# Once the Order is created, Items should not be Updated.
# For this, Cancel the Previous Order and Create a New One with Correct Information.
