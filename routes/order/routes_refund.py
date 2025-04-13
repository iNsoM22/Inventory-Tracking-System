from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from uuid import UUID
from utils.db import db_dependency
from schemas.order import Order
from schemas.refund import Refund, RefundItems
from validations.refund import (
    RefundRequest,
    RefundUpdateRequest,
    RefundResponse,
    ALLOWED_TRANSITIONS
)
from utils.check_inventory import check_and_add_inventory
from utils.auth import user_dependency, require_access_level
from utils.create_transaction import add_transaction


router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.post("/add",
             response_model=RefundResponse,
             status_code=status.HTTP_201_CREATED)
def create_refund(refund_data: RefundRequest,
                  db: db_dependency,
                  current_user: user_dependency):
    try:
        order = db.query(Order).filter(
            Order.id == refund_data.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order Not Found")

        refund_data.validate_application(order)
        amount = refund_data.amount or refund_data.calculate_total_amount(
            order)

        refund_items = [RefundItems(product_id=item.product_id,
                                    quantity=item.quantity) for item in refund_data.items]
        new_refund = Refund(
            reason=refund_data.reason,
            amount=amount,
            status=refund_data.status,
            application_date=refund_data.application_date,
            order_id=refund_data.order_id,
            items=refund_items
        )

        if not current_user["is_internal_user"] and refund_data.status != "Pending":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only Internal Users are allowed to have refund application status other than Pending")

        if refund_data.status == "Refunded":
            order.status = "Refunded"
            check_and_add_inventory(new_refund, operation_type="Sale", db=db)
            add_transaction(new_refund, current_user["id"], db)

        else:
            order.status = "For Refund"

        db.add(new_refund)
        db.commit()
        db.refresh(new_refund)

        return RefundResponse.model_validate(new_refund)

    except HTTPException as e:
        raise e

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Creating Refund Application: {str(e)}")


@router.get("/get/{refund_id}",
            response_model=RefundResponse,
            status_code=status.HTTP_200_OK)
def get_refund(refund_id: UUID,
               db: db_dependency,
               current_user: user_dependency):
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Refund Application Not Found")

        if not current_user["is_internal_user"] and refund.order.customer.user_id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only the Customer or Internal Users are allowed to view Refund Applications")
        return RefundResponse.model_validate(refund)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Refund Record: {str(e)}")


@router.get("/all",
            response_model=List[RefundResponse],
            status_code=status.HTTP_200_OK)
def get_all_refunds(db: db_dependency,
                    current_user: Annotated[dict, Depends(require_access_level(3))],
                    limit: int = 100,
                    offset: int = 0):
    try:
        refunds = (
            db.query(Refund)
            .order_by(Refund.application_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [RefundResponse.model_validate(refund) for refund in refunds]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Refund Records: {str(e)}")


@router.put("/mod/{refund_id}",
            response_model=RefundResponse,
            status_code=status.HTTP_202_ACCEPTED)
def update_refund(refund_id: UUID,
                  update_data: RefundUpdateRequest,
                  db: db_dependency,
                  current_user: user_dependency):
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(
                status_code=404, detail="Refund Application Not Found")

        if update_data.status and update_data.status not in ALLOWED_TRANSITIONS[refund.status]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Invalid Status Transition")

        if update_data.status:
            refund.status = update_data.status
            refund.date_refunded = update_data.date_refunded

        if update_data.reason:
            refund.reason = update_data.reason

        if update_data.status != "Cancelled" and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only Internal Users are allowed to Update Refund Applications")

        if update_data.status == "Refunded":
            refund.order.status = "Refunded"
            add_transaction(refund, current_user["id"], db)
            check_and_add_inventory(refund, operation_type="Sale", db=db)

        db.commit()
        db.refresh(refund)
        return RefundResponse.model_validate(refund)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Updating Refund Application: {str(e)}")


@router.delete("/del/{refund_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_refund(refund_id: UUID, db: db_dependency,
                  current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Delete a Refund Application, Usage is highly Discouraged. 
        Use Update End-Point for Managing Application."""
    try:
        refund = db.query(Refund).filter(Refund.id == refund_id).first()
        if not refund:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Refund Not Found")

        db.delete(refund)
        db.commit()
        return

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Deleting Refund Application: {str(e)}")


# P.S: Once the Application is submitted, the Items selected for the Refund as well as their
# respective quantities cannot be changed. For this, Cancel the Previous Application and Submit a
# new one. Also, the Delete End-Point is discouraged for usage due to Inventory Auditing issues.
