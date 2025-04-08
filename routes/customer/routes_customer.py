from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from validations.customer import (
    CustomerRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    CustomerUserIDUpdateRequest
)
from validations.order import OrderResponse
from validations.refund import RefundResponse
from utils.db import db_dependency
from schemas.customer import Customer
from schemas.order import Order
from schemas.refund import Refund


router = APIRouter(prefix="/customers")


@router.post("/add",
             response_model=List[CustomerResponse],
             status_code=status.HTTP_201_CREATED)
async def add_customers(customers: List[CustomerRequest], db: db_dependency):
    """Add New Customers."""
    try:
        new_customers = [Customer(**customer.model_dump())
                         for customer in customers]
        db.add_all(new_customers)
        db.commit()

        db.refresh(new_customers)
        return [CustomerResponse.model_validate(cust) for cust in new_customers]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Adding Customers: {str(e)}")


@router.get("/all",
            response_model=List[CustomerResponse],
            status_code=status.HTTP_200_OK)
async def get_customers(db: db_dependency, limit: int = 10, offset: int = 0):
    """Get All Customers."""
    try:
        customers = db.query(Customer).offset(offset).limit(limit).all()
        return [CustomerResponse.model_validate(customer) for customer in customers]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Customers: {str(e)}")


@router.get("/get/{customer_id}",
            response_model=CustomerResponse,
            status_code=status.HTTP_200_OK)
async def get_customer(customer_id: UUID, db: db_dependency):
    """Get a Customer by ID."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        return CustomerResponse.model_validate(customer)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Customer: {str(e)}")


@router.put("/mod/{customer_id}",
            response_model=CustomerResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_customer(customer_id: UUID, update_data: CustomerUpdateRequest, db: db_dependency):
    """Update a Customer by ID."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)

        db.commit()
        db.refresh(customer)
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
                                  db: db_dependency):
    """Update Customer's User ID."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        customer.user_id = new_data.user_id
        db.commit()
        db.refresh(customer)
        return CustomerResponse.model_validate(customer)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating User ID: {str(e)}")


@router.delete("/del/{customer_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: UUID, db: db_dependency):
    """Delete a Customer by ID."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        db.delete(customer)
        db.commit()

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Customer: {str(e)}")


@router.get("/orders/{customer_id}",
            status_code=status.HTTP_200_OK)
async def get_customer_orders(customer_id: UUID, db: db_dependency):
    """Get a Customer's Orders."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        customer_response = CustomerResponse.model_validate(customer)
        orders = (
            db.query(Order)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.date_placed.desc())
            .all()
        )
        customer_response.orders = [
            OrderResponse.model_validate(order) for order in orders]
        return customer_response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Orders: {str(e)}")


@router.get("/refunds/{customer_id}",
            status_code=status.HTTP_200_OK)
async def get_customer_refunds(customer_id: UUID, db: db_dependency):
    """Get a Customer's Refunds."""
    try:
        customer = db.query(Customer).filter(
            Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Customer Not Found")

        customer_response = CustomerResponse.model_validate(customer)
        refunds = (
            db.query(Refund)
            .join(Order, Order.id == Refund.order_id)
            .filter(Order.customer_id == customer_id)
            .order_by(Refund.date_placed.desc())
            .all()
        )
        customer_response.refunds = [
            RefundResponse.model_validate(refund) for refund in refunds
        ]
        return customer_response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Fetching Refunds: {str(e)}")
