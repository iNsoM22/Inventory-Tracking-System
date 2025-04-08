from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID4
from datetime import datetime, timezone
from typing import Optional


class EmployeeBase(BaseModel):
    first_name: str = Field(
        ...,
        max_length=30,
        description="First Name of the Employee"
    )
    last_name: str = Field(
        ...,
        max_length=30,
        description="Last Name of the Employee"
    )
    phone_number: str = Field(
        ...,
        max_length=16,
        description="Phone number of the Employee"
    )
    email: EmailStr = Field(
        ...,
        description="Email of the Employee"
    )
    address: str = Field(
        ...,
        max_length=200,
        description="Address of the Employee"
    )
    hire_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Hire Date of the Employee"
    )
    leave_date: Optional[datetime] = Field(
        None,
        description="Leave Date of the Employee"
    )
    user_id: UUID4 = Field(
        ...,
        description="(F.K) Unique Identifier for the User ID"
    )

    model_config = ConfigDict(from_attributes=True)


class EmployeeRequest(EmployeeBase):
    store_id: UUID4 = Field(
        ...,
        description="Store Identifier where the Employee Works"
    )


class EmployeeResponse(EmployeeBase):
    id: UUID4 = Field(
        ...,
        description="Unique Identifier for the Employee"
    )
    store_id: UUID4 = Field(
        ...,
        description="Store Identifier where the Employee Works"
    )


class EmployeeResponseWithOutStore(EmployeeResponse):
    store_id: UUID4 = Field(
        exclude=True,
        default=None,
        description="Store Identifier where the Employee Works"
    )


class EmployeeUpdateRequest(BaseModel):
    id: UUID4 = Field(
        ...,
        description="Unique Identifier for the Employee"
    )
    first_name: Optional[str] = Field(
        None,
        max_length=30,
        description="First Name of the Employee"
    )
    last_name: Optional[str] = Field(
        None,
        max_length=30,
        description="Last Name of the Employee"
    )
    hire_date: Optional[datetime] = Field(
        None,
        description="Hire Date of the Employee"
    )
    leave_date: Optional[datetime] = Field(
        None,
        description="Leave Date of the Employee"
    )
    phone_number: Optional[str] = Field(
        None,
        max_length=16,
        description="Phone number of the Employee"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Email of the Employee"
    )
    address: Optional[str] = Field(
        None,
        max_length=200,
        description="Address of the Employee"
    )
    store_id: Optional[UUID4] = Field(
        None,
        description="Store Identifier where the Employee Works"
    )

    model_config = ConfigDict(from_attributes=True)


class EmployeeUserIDUpdateRequest(BaseModel):
    user_id: UUID4 = Field(
        ...,
        description="User ID for the Employee"
    )
    new_user_id: UUID4 = Field(
        ...,
        description="New User ID for the Employee"
    )


class EmployeeDeleteRequest(BaseModel):
    id: UUID4 = Field(
        ...,
        description="Unique Identifier for the Employee"
    )
