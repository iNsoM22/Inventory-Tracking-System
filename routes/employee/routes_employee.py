from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from validations.employee import (
    EmployeeRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
    EmployeeDeleteRequest,
    EmployeeUserIDUpdateRequest
)
from utils.db import db_dependency
from schemas.employee import Employee


router = APIRouter(prefix="/management")


@router.post("/employee/add",
             response_model=List[EmployeeResponse],
             status_code=status.HTTP_201_CREATED)
async def add_employees(employees: List[EmployeeRequest], db: db_dependency):
    """Create a new Employee."""
    try:
        new_employees = [Employee(**employee.model_dump())
                         for employee in employees]
        db.add_all(new_employees)
        db.commit()
        db.refresh(new_employees)

        return [EmployeeResponse.model_validate(emp) for emp in new_employees]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Creating Employees: {str(e)}")


@router.get("/employee/get/{employee_id}",
            response_model=EmployeeResponse,
            status_code=status.HTTP_200_OK)
async def get_employee_by_id(employee_id: UUID, db: db_dependency):
    """Get Employee details."""
    try:
        employee = db.query(Employee).filter(
            Employee.id == employee_id).first()

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employee Not Found")

        return EmployeeResponse.model_validate(employee)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Fetching Employee: {str(e)}")


@router.get("/employee/all",
            response_model=List[EmployeeResponse],
            status_code=status.HTTP_200_OK)
async def get_all_employees(db: db_dependency, limit: int = 10, offset: int = 0):
    """Get all Employee details."""
    try:
        employees = db.query(Employee).offset(offset).limit(limit).all()
        return [EmployeeResponse.model_validate(emp) for emp in employees]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Fetching Employees: {str(e)}")


@router.put("/employee/mod",
            response_model=List[EmployeeResponse],
            status_code=status.HTTP_202_ACCEPTED)
async def update_employee(employees_data: List[EmployeeUpdateRequest], db: db_dependency):
    """Update Existing Employees."""
    try:
        update_map = {emp.id: emp for emp in employees_data}
        employees = db.query(Employee).filter(
            Employee.id.in_(update_map)).all()

        if not employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employees Not Found")

        for emp in employees:
            update = update_map.get(emp.id)
            if update.first_name:
                emp.first_name = update.first_name
            if update.last_name:
                emp.last_name = update.last_name
            if update.phone_number:
                emp.phone_number = update.phone_number
            if update.email:
                emp.email = update.email
            if update.address:
                emp.address = update.address
            if update.store_id:
                emp.store_id = update.store_id
            if update.hire_date:
                emp.hire_date = update.hire_date
            if update.leave_date:
                emp.leave_date = update.leave_date

        db.commit()
        db.refresh(employees)

        return [EmployeeResponse.model_validate(emp) for emp in employees]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Employee: {str(e)}")


@router.put("/employee/mod/{employee_id}",
            response_model=EmployeeResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_employee_user_id(employee_id: UUID, new_data: EmployeeUserIDUpdateRequest, db: db_dependency):
    """Update User ID for a Specific Employee."""
    try:
        employee = db.query(Employee).filter(
            Employee.id == employee_id).first()

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employee Not Found")

        employee.user_id = new_data.user_id
        db.commit()
        db.refresh(employee)

        return EmployeeResponse.model_validate(employee)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Employee User ID: {str(e)}")


@router.delete("/employee/del",
               status_code=status.HTTP_202_ACCEPTED)
async def delete_employee(employees_for_deletion: List[EmployeeDeleteRequest], db: db_dependency):
    """Delete Employees."""
    try:
        delete_ids = [emp.id for emp in employees_for_deletion]
        employees = db.query(Employee).filter(
            Employee.id.in_(delete_ids)).all()

        if not employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employees Not Found")

        for emp in employees:
            db.delete(emp)

        db.commit()

        return {"detail": "Employees and Related Information have been deleted Successfully."}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Employee: {str(e)}")
