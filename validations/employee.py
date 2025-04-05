from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, computed_field, UUID4
from datetime import datetime, timezone
from typing import Optional, List


class RoleBase(BaseModel):
    level: int = Field(..., description="Role Level for Access")
    role: str = Field(..., description="Role Name")

    model_config = ConfigDict(from_attributes=True)


class RoleRequest(RoleBase):
    pass


class RoleUpdateRequest(BaseModel):
    level: int = Field(..., description="Role Level for Access")
    role: Optional[str] = Field(..., description="Role Name")

    model_config = ConfigDict(from_attributes=True)

class RoleDeleteRequest(BaseModel):
    level: int = Field(..., description="Role Level for Access")


class RoleResponse(RoleBase):
    pass

    
class RoleResponseWithEmployees(RoleBase):
    employees: List[dict] = Field(
        default=None, description="List of Employees Associated with this Role")
    
    @field_validator(field="employees", mode="before")
    def format_employees(cls, values: List["EmployeeBase"]):
        return [employee.model_dump(exclude=["store_id", "level"]) for employee in values]
    
    @computed_field
    @property
    def employee_count(self) -> int:
        return len(self.employees) if self.employees else 0
    


class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=30, description="First Name of the Employee")
    last_name: str = Field(..., max_length=30, description="Last Name of the Employee")
    phone_number: str = Field(..., max_length=16, description="Phone number of the Employee")
    email: EmailStr = Field(..., description="Email of the Employee")
    address: str = Field(..., max_length=200, description="Address of the Employee")
    level: int = Field(..., description="Employee Role Level from Roles")
    hire_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), 
                                description="Hire Date of the Employee")
    leave_date: Optional[datetime] = Field(None, description="Leave Date of the Employee")
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeRequest(EmployeeBase):
    store_id: UUID4 = Field(..., description="Store Identifier where the Employee Works")



class EmployeeResponse(EmployeeBase):
    id: UUID4 = Field(..., description="Unique Identifier for the Employee")
    store_id: UUID4 = Field(..., description="Store Identifier where the Employee Works")
    role: str = Field(..., description="Role of the Employee")
    
    @field_validator(field='role', mode="before")
    def validate_role_format(cls, value: RoleBase):
        return value.role



class EmployeeUpdateRequest(BaseModel):
    id: UUID4 = Field(..., description="Unique Identifier for the Employee")
    first_name: Optional[str] = Field(None, max_length=30, description="First Name of the Employee")
    last_name: Optional[str] = Field(None, max_length=30, description="Last Name of the Employee")
    hire_date: Optional[datetime] = Field(None, description="Hire Date of the Employee")
    leave_date: Optional[datetime] = Field(None, description="Leave Date of the Employee")
    phone_number: Optional[str] = Field(None, max_length=16, description="Phone number of the Employee")
    email: Optional[EmailStr] = Field(None, description="Email of the Employee")
    address: Optional[str] = Field(None, max_length=200, description="Address of the Employee")
    level: Optional[UUID4] = Field(None, description="Role Level Identifier")
    store_id: Optional[UUID4] = Field(None, description="Store Identifier where the Employee Works")
    
    model_config = ConfigDict(from_attributes=True)

class EmployeeDeleteRequest(BaseModel):
    id: UUID4 = Field(..., description="Unique Identifier for the Employee")
    