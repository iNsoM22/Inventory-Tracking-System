from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(min_length=7, max_length=20, example="Username to be used in the Account")
    is_internal_user: Optional[bool] = Field(False, description="Set true for Employees")
    
    model_config = ConfigDict(from_attributes=True)



class UserRequest(UserBase):
    password: str = Field(min_length=9, max_length=100, description="Password for the User Account")




class UserLoginRequest(BaseModel):
    username: str = Field(min_length=7, max_length=20, example="Username to be used in the Account")
    password: str = Field(min_length=9, max_length=100, description="Password for the User Account")
    


class UserPasswordUpdateRequest(UserLoginRequest):
    new_password: str = Field(min_length=9, max_length=100, description="New Password for the User Account")
    


class UserRead(UserBase):
    id: UUID = Field(..., description="Unique Identifier for the User")
    created_at: datetime = Field(..., description="Timestamp when the User was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the User was last updated")