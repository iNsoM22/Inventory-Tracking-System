from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
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
from utils.auth import require_access_level
from schemas.user import User


router = APIRouter(prefix="/employees", tags=["Employee Management"])


@router.post("/add",
             response_model=List[EmployeeResponse],
             status_code=status.HTTP_201_CREATED)
async def add_employees(employees: List[EmployeeRequest], db: db_dependency,
                        current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Create a new Employee."""
    try:
        new_employees = [Employee(**employee.model_dump())
                         for employee in employees]
        db.add_all(new_employees)
        db.commit()
        response = []
        for emp in new_employees:
            db.refresh(emp)
            response.append(EmployeeResponse.model_validate(emp))

        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Creating Employees: {str(e)}")


@router.get("/get/{employee_id}",
            response_model=EmployeeResponse,
            status_code=status.HTTP_200_OK)
async def get_employee_by_id(employee_id: UUID, db: db_dependency,
                             current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Get Employee details."""
    try:
        employee = (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employee Not Found")

        return EmployeeResponse.model_validate(employee)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Fetching Employee: {str(e)}")


@router.get("/all",
            response_model=List[EmployeeResponse],
            status_code=status.HTTP_200_OK)
async def get_all_employees(db: db_dependency,
                            current_user: Annotated[dict, Depends(require_access_level(3))],
                            limit: int = 10,
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

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Fetching Employees: {str(e)}")


@router.put("/mod",
            response_model=List[EmployeeResponse],
            status_code=status.HTTP_202_ACCEPTED)
async def update_employee(employees_data: List[EmployeeUpdateRequest], db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Update Existing Employees."""
    try:
        employees_to_update = {emp.id: emp for emp in employees_data}
        employees = (
            db.query(Employee)
            .filter(Employee.id.in_(employees_to_update))
            .all()
        )

        if not employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employees Not Found")

        for employee in employees:
            updated_employee: EmployeeUpdateRequest = employees_to_update[employee.id]
            for field, value in updated_employee.model_dump(exclude_unset=True).items():
                setattr(employee, field, value)

        db.commit()
        response = []
        for emp in employees:
            db.refresh(emp)
            response.append(EmployeeResponse.model_validate(emp))

        return response

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Employee: {str(e)}")


@router.put("/mod/user-id/{employee_id}",
            response_model=EmployeeResponse,
            status_code=status.HTTP_202_ACCEPTED)
async def update_employee_user_id(employee_id: UUID,
                                  new_data: EmployeeUserIDUpdateRequest,
                                  db: db_dependency,
                                  current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Update User ID for a Specific Employee."""
    try:
        employee = (
            db.query(Employee).
            filter(Employee.id == employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employee Not Found")

        if current_user["id"] == employee.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Cannot Update Your Own User ID")
        if new_data.new_user_id:
            user = db.query(User).filter(
                User.id == new_data.new_user_id).first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="User Not Found, Create a User Account First to Assign the User ID")

            if user.level > current_user["level"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Cannot Assign User ID to a User with a Higher Access Level")

        employee.user_id = new_data.user_id
        db.commit()
        db.refresh(employee)
        # P.S: Logout User after Changing its Credentials
        return EmployeeResponse.model_validate(employee)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Error Updating Employee User ID: {str(e)}")


@router.delete("/del",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employees_for_deletion: List[EmployeeDeleteRequest], db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(4))]):
    """Delete Employees."""
    try:
        delete_ids = [emp.id for emp in employees_for_deletion]
        employees = db.query(Employee).filter(
            Employee.id.in_(delete_ids)).all()

        if not employees:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Employees Not Found")

        for emp in employees:
            if emp.user.level < current_user["level"]:
                db.delete(emp)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Cannot Delete Higher Level Employee Accounts")

        db.commit()
        return

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Employee: {str(e)}")
