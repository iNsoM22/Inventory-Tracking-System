from fastapi import APIRouter, HTTPException
from typing import List
from validations.customer import CustomerRequest, CustomerResponse, CustomerUpdateRequest
from utils.db import db_dependency
from schemas.customer import Customer
from uuid import UUID


router = APIRouter(prefix="/customers")


@router.post("/add", response_model=List[CustomerResponse])
async def add_customers(customers: List[CustomerRequest], db: db_dependency):
    """Add a New Customer."""
    try:
        new_customers = [Customer(**customer.model_dump()) for customer in customers]
        db.add_all(new_customers)
        db.commit()
        
        for customer in new_customers:
            db.refresh(customer)
        return [CustomerResponse.model_validate(cust) for cust in new_customers]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Adding Customers: {str(e)}")

@router.get("/all", response_model=List[CustomerResponse])
async def get_customers(limit: int | None, offset: int | None, db: db_dependency):
    """Get All Customers from the Database."""
    try:
        def_offset = 0 if not offset else offset
        def_limit = 10 if not limit else limit
        customers = db.query(Customer).offset(def_offset).limit(def_limit).all()
        return [CustomerResponse.model_validate(customer) for customer in customers]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Customer Records: {str(e)}")
    

@router.get("/get/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: UUID, db: db_dependency):
    """Get a Customer using its ID."""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer Not Found")
        return CustomerResponse.model_validate(customer)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Fetching Customer: {str(e)}")
    

@router.put("/mod/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: UUID, update_data: CustomerUpdateRequest, db: db_dependency):
    """Update a Customer by ID."""
    try:
        customer_to_update = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer_to_update:
            raise HTTPException(status_code=404, detail="Customer Not Found")

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(customer_to_update, field, value)

        db.commit()
        db.refresh(customer_to_update)
        return CustomerResponse.model_validate(customer_to_update)

    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Customer: {str(e)}")


@router.delete("/del/{customer_id}", response_model=CustomerResponse)
async def delete_customer(customer_id: UUID, db: db_dependency):
    """Delete a Customer by ID."""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            db.delete(customer)
            db.commit()

            return CustomerResponse.model_validate(customer)
        raise HTTPException(status_code=404, detail="Customer Not Found")
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Customer: {str(e)}")
    

# Create an End-Point for Customer and its History (Orders, Refunds).