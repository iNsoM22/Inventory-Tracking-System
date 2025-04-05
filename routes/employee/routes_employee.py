from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from validations.employee import EmployeeRequest, EmployeeResponse, EmployeeUpdateRequest, EmployeeDeleteRequest
from utils.db import db_dependency 
from schemas.employee import Employee


router = APIRouter(prefix="/management")

@router.post("/employee/add", response_model=List[EmployeeResponse])
async def add_employees(employees: List[EmployeeRequest], db: db_dependency):
    """Create a new Employee."""
    try:
        new_employees = [Employee(**employee.model_dump()) for employee in employees]
        db.add_all(new_employees)
        db.commit()
        
        db.refresh(new_employees)
        
        return [EmployeeResponse.model_validate(new_employee) for new_employee in new_employees]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Creating Employees: {str(e)}")


@router.get("/employee/get/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(employee_id: UUID, db: db_dependency):
    """Get Employee details."""
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise HTTPException(status_code=404, detail="Employee Not Found")
        
        return EmployeeResponse.model_validate(employee)
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Employee: {str(e)}")


@router.get("/employee/all", response_model=List[EmployeeResponse])
async def get_all_employees(db: db_dependency, limit: int=10, offset: int=0):
    """Get Employee details."""
    try:
        employees = db.query(Employee).offset(offset).limit(limit).all()
        return [EmployeeResponse.model_validate(employee) for employee in employees]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Employees: {str(e)}")


@router.put("/employee/mod", response_model=List[EmployeeResponse])
async def update_employee(employees_data: List[EmployeeUpdateRequest], db: db_dependency):
    """Update Existing Employees."""
    try:
        employee_to_update_dict = {employee.id: employee for employee in employees_data}
        employees = db.query(Employee).filter(Employee.id.in_(employee_to_update_dict.keys())).all()
        
        if not employees:
            raise HTTPException(status_code=404, detail="Employees Not Found")
        
        for employee in employees:
            employee_data: EmployeeUpdateRequest = employee_to_update_dict.get(employee.id)
                        
            if employee_data.first_name:
                employee.first_name = employee_data.first_name
            if employee_data.last_name:
                employee.last_name = employee_data.last_name
            if employee_data.phone_number:
                employee.phone_number = employee_data.phone_number
            if employee_data.email:
                employee.email = employee_data.email
            if employee_data.address:
                employee.address = employee_data.address
            if employee_data.level:
                employee.level = employee_data.level
            if employee_data.store_id:
                employee.store_id = employee_data.store_id
            if employee_data.hire_date:
                employee.hire_date = employee_data.hire_date
            if employee_data.leave_date:
                employee.leave_date = employee_data.leave_date
        
        db.commit()
        db.refresh(employees)
        
        return [EmployeeResponse.model_validate(employee) for employee in employees]
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Employee: {str(e)}")


@router.delete("/employee/del", status_code=204)
async def delete_employee(employees_for_deletion: List[EmployeeDeleteRequest], db: db_dependency):
    """Delete Employees."""
    try:
        employee_to_delete_ids = [employee.id for employee in employees_for_deletion]
        employees = db.query(Employee).filter(Employee.id.in_(employee_to_delete_ids)).all()
        
        if not employees:
            raise HTTPException(status_code=404, detail="Employees Not Found")
        
        for employee in employees:
            db.delete(employee)
        
        db.commit()
        
        return {"detail": "Employees and Related Information have been deleted Successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Employee: {str(e)}")
