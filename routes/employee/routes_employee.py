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
async def get_all_employees(db: db_dependency, limit: int = 10,
                            offset: int = 0, by_position: str | None = None):
    """Get all Employee details."""
    try:
        if by_position:
            employees = (
                db.query(Employee)
                .filter(Employee.position == by_position)
                .offset(offset)
                .limit(limit)
                .all()
            )
        else:
            employees = (
                db.query(Employee)
                .offset(offset)
                .limit(limit)
                .all()
            )
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
        employees_to_update = {emp.id: emp for emp in employees_data}
        employees = db.query(Employee).filter(
            Employee.id.in_(employees_to_update)).all()

        if not employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employees Not Found")

        for employee in employees:
            updated_employee: EmployeeUpdateRequest = employees_to_update[employee.id]
            for field, value in updated_employee.model_dump(exclude_unset=True).items():
                setattr(employee, field, value)

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
