from pydantic import BaseModel, Field, ConfigDict, computed_field
from uuid import UUID
from typing import Optional, List


class RoleRequest(BaseModel):
    level: int = Field(..., description="Role Level for Access")
    role: str = Field(..., description="Role Name")


class RoleResponse(BaseModel):
    level: int = Field(..., description="Role Level of the Employee")
    role: str = Field(..., description="Role Name")
    
    model_config = ConfigDict(from_attributes=True)
    
    
class RoleResponseWithEmployees(RoleResponse):
    employees: Optional[List[UUID]] = Field(
        default=None, description="List of Employee IDs associated with this Role")
    
    @computed_field
    @property
    def employee_count(self) -> int:
        return len(self.employees) if self.employees else 0