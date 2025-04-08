from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import List
from .user import UserPublicResponse


class RoleBase(BaseModel):
    level: int = Field(
        ...,
        description="Role Level for Role Based Access Control"
    )
    role: str = Field(
        ...,
        description="Name of the Role"
    )

    model_config = ConfigDict(from_attributes=True)


class RoleRequest(RoleBase):
    pass


class RoleUpdateRequest(RoleBase):
    pass


class RoleDeleteRequest(BaseModel):
    level: int = Field(
        ...,
        description="Role Level for Access"
    )


class RoleResponse(RoleBase):
    pass


class RoleResponseWithUsers(RoleBase):
    users: List["UserPublicResponse"] = Field(
        default=list,
        description="List of Users Associated with the Role"
    )

    @computed_field
    @property
    def user_count(self) -> int:
        return len(self.users)
