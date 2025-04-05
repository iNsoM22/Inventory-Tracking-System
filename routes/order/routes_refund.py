from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from utils.db import db_dependency
from schemas.order import Order
from schemas.refund import Refund, RefundItems
from validations.refund import (
    RefundRequest,
    RefundUpdateRequest,
    RefundResponse,
)


router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.post("/add", response_model=RefundResponse)
def create_refund(refund_data: RefundRequest, db: db_dependency):
    try:
        order = db.query(Order).filter(Order.id == refund_data.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")

        refund_data.validate_application(order)
        if refund_data.amount:
            products_ordered = {p.product_id: p for p in order.items}
            total_amount = 0
            refund_items = []
            for item in refund_data.items:
                if item.product_id in products_ordered:
                    product = products_ordered[item.product_id]
                    price = product.product.price * (1 - product.discount)
                    total_amount += price * item.quantity
                    refund_model = RefundItems(
                        product_id=item.product_id,
                        quantity=item.quantity
                    )
                    refund_items.append(refund_model)
        else:
            refund_items = [
                RefundItems(
                    product_id=item.product_id,
                    quantity=item.quantity
                ) for item in refund_data.items
            ]

        new_refund = Refund(
            reason=refund_data.reason,
            amount=refund_data.amount or total_amount,
            status=refund_data.status,
            application_date=refund_data.application_date,
            order_id=refund_data.order_id,
            items=refund_items
        )
        
        order.status = "For Refund"

        db.add(new_refund)
        db.commit()
        db.refresh(new_refund)

        return RefundResponse.model_validate(new_refund)
    
    except HTTPException as e:
        raise e
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Creating Refund Application: {str(e)}")
    

@router.get("/get/{refund_id}", response_model=RefundResponse)
def get_refund(refund_id: UUID, db: db_dependency):
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(status_code=404, detail="Refund Application Not Found")
        return RefundResponse.model_validate(refund)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Refund Record: {str(e)}")


@router.get("/all", response_model=List[RefundResponse])
def get_all_refunds(db: db_dependency):
    try:
        refunds = db.query(Refund).all()
        return [RefundResponse.model_validate(refund) for refund in refunds]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Refund Records: {str(e)}")


@router.put("/mod/{refund_id}", response_model=RefundResponse)
def update_refund(refund_id: UUID, update_data: RefundUpdateRequest, db: db_dependency):
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(status_code=404, detail="Refund Application Not Found")

        if update_data.status:
            refund.status = update_data.status
            refund.date_refunded = update_data.date_refunded
            
        if update_data.reason:
            refund.reason = update_data.reason

        db.commit()
        db.refresh(refund)
        return RefundResponse.model_validate(refund)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Refund Application: {str(e)}")


@router.delete("/del/{refund_id}", status_code=204)
def delete_refund(refund_id: UUID, db: db_dependency):
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(status_code=404, detail="Refund Not Found")

        db.delete(refund)
        db.commit()
        return {"detail": "Refund Application Deleted Successfully."}
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Refund Application: {str(e)}")


# P.S: Once the Application is submitted, the Items selected for the Refund as well as their 
# respective quantities cannot be changed. For this, Cancel the Previos Application and Submit a
# new one.