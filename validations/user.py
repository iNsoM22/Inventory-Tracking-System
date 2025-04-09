from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="User Access Token for JWT"
    )
    token_type: str = Field(
        ...,
        description="Type of the Token"
    )


class UserBase(BaseModel):
    username: str = Field(
        min_length=7,
        max_length=20,
        description="Username to be used in the Account")
    level: int = Field(
        default=1,
        description="Role Level of the User (Requires Special Priveledges to Use a High Level)"
    )
    is_internal_user: Optional[bool] = Field(
        default=False,
        description="Indicates if the User is an Employee or a Customer"
    )

    model_config = ConfigDict(from_attributes=True)


class UserRequest(UserBase):
    password: str = Field(
        min_length=9,
        max_length=100,
        description="Password for the User Account"
    )


class UserLoginRequest(BaseModel):
    username: str = Field(
        min_length=7,
        max_length=20,
        example="Username to be used in the Account"
    )
    password: str = Field(
        min_length=9,
        max_length=100,
        description="Password for the User Account"
    )


class UserPasswordUpdateRequest(UserLoginRequest):
    new_password: str = Field(
        min_length=9,
        max_length=100,
        description="New Password for the User Account"
    )


class UserRead(UserBase):
    id: UUID = Field(
        ...,
        description="Unique Identifier for the User"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the User was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the User was last updated"
    )


class UserPublicResponse(UserBase):
    id: UUID = Field(
        ...,
        description="Unique Identifier for the User"
    )
