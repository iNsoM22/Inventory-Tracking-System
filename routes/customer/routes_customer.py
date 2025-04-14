from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from uuid import UUID
from sqlalchemy.future import select
from validations.customer import (
    CustomerRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    CustomerUserIDUpdateRequest
)
from validations.order import OrderResponse
from validations.refund import RefundResponse
from utils.db import db_dependency
from schemas.user import User
from schemas.customer import Customer
from schemas.order import Order
from schemas.refund import Refund
from utils.auth import require_access_level, user_dependency


router = APIRouter(prefix="/customers")


@router.post("/add",
             response_model=CustomerResponse,
             status_code=status.HTTP_201_CREATED)
async def add_customers(customer: CustomerRequest, db: db_dependency,
                        current_user: user_dependency):
    """Add New Customer."""
    try:
        new_customer = Customer(**customer.model_dump())
        if current_user["is_internal_user"]:
            new_customer.user_id = None

        if current_user["id"] != customer.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Unable to Create Customer with differing User IDs")

        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)
        return CustomerResponse.model_validate(new_customer)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Adding Customers: {str(e)}")


@router.get("/all",
            response_model=List[CustomerResponse],
            status_code=status.HTTP_200_OK)
async def get_customers(db: db_dependency,
                        current_user: Annotated[dict, Depends(require_access_level(2))],
                        limit: int = 10, offset: int = 0):
    """Get All Customers."""
    try:
        stmt = select(Customer).offset(offset).limit(limit)
        result = await db.execute(stmt)
        customers = result.scalars().all()
        return [CustomerResponse.model_validate(customer) for customer in customers]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Customers: {str(e)}")


@router.get("/get/{customer_id}",
            response_model=CustomerResponse,
            status_code=status.HTTP_200_OK)
async def get_customer(customer_id: UUID, db: db_dependency,
                       current_user: user_dependency):
    """Get a Customer by ID."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Unable to Retrieve Customer with Differing User IDs")

        return CustomerResponse.model_validate(customer)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Customer: {str(e)}")


@router.put("/mod/{customer_id}",
            response_model=CustomerResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_customer(customer_id: UUID, updated_data: CustomerUpdateRequest,
                          db: db_dependency, current_user: user_dependency):
    """Update a Customer by ID."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Unable to Retrieve Customer with Differing User IDs")

        for field, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)

        await db.commit()
        await db.refresh(customer)
        return CustomerResponse.model_validate(customer)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Customer: {str(e)}")


@router.put("/mod/id/{customer_id}",
            response_model=CustomerResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_customer_user_id(customer_id: UUID,
                                  new_data: CustomerUserIDUpdateRequest,
                                  db: db_dependency,
                                  current_user: Annotated[dict, Depends(require_access_level(2))]):
    """Update Customer's User ID."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()

        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if new_data.user_id == current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Cannot Update Customer's User ID to Current User's ID")
        
        stmt = select(User).where(User.id == new_data.user_id)
        user_result = await db.execute(stmt)
        user = user_result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User Account Not Found")

        customer.user_id = new_data.user_id
        await db.commit()
        await db.refresh(customer)
        return CustomerResponse.model_validate(customer)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating User ID: {str(e)}")


@router.delete("/del/{customer_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: UUID, db: db_dependency,
                          current_user: user_dependency):
    """Delete a Customer by ID."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Cannot Delete Customer Account")

        if current_user["is_internal_user"]:
            user = db.query(User).filter(User.id == current_user["id"]).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Current User Account Not Verifiable")

            if user.level < 3:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Cannot Delete Customer Account, Minimum Access Level should be 3")

        await db.delete(customer)
        await db.commit()

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Customer: {str(e)}")


@router.get("/orders/{customer_id}",
            status_code=status.HTTP_200_OK)
async def get_customer_orders(customer_id: UUID, db: db_dependency,
                              current_user: user_dependency):
    """Get a Customer's Orders."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        customer_response = CustomerResponse.model_validate(customer)
        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Unable to Retrieve Customer, IDs are not matched.")

        stmt = select(Order).where(Order.customer_id == customer_id).order_by(Order.date_placed.desc())
        order_result = await db.execute(stmt)
        orders = order_result.scalars().all()

        customer_response.orders = [OrderResponse.model_validate(order) for order in orders]
        return customer_response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Orders: {str(e)}")


@router.get("/refunds/{customer_id}",
            status_code=status.HTTP_200_OK)
async def get_customer_refunds(customer_id: UUID, db: db_dependency,
                               current_user: user_dependency):
    """Get a Customer's Refunds."""
    try:
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalars().first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        if current_user["id"] != customer.user_id and not current_user["is_internal_user"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Unable to Retrieve Customer, IDs are not matched.")

        customer_response = CustomerResponse.model_validate(customer)
        stmt = (
            select(Refund)
            .join(Order, Refund.order_id == Order.id)
            .where(Order.customer_id == customer_id)
            .order_by(Refund.date_placed.desc())
            )
        refund_result = await db.execute(stmt)
        refunds = refund_result.scalars().all()
        customer_response.refunds = [RefundResponse.model_validate(refund) for refund in refunds]
        return customer_response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Refunds: {str(e)}")
