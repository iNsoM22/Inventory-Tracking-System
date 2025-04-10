from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from validations.role import (
    RoleRequest,
    RoleResponse,
    RoleResponseWithUsers,
    RoleUpdateRequest,
    RoleDeleteRequest)
from utils.db import db_dependency
from schemas.role import Role
from utils.auth import user_dependency, require_access_level


router = APIRouter(prefix="/management")


@router.post("/role/add",
             response_model=List[RoleResponse],
             status_code=status.HTTP_201_CREATED)
async def create_role(roles: List[RoleRequest], db: db_dependency,
                      current_user: Annotated[dict, Depends(require_access_level(5))]):
    """Create a New Role."""
    try:
        new_roles = [Role(**role.model_dump()) for role in roles]
        db.add_all(new_roles)
        db.commit()

        return [RoleResponse.model_validate(new_role) for new_role in new_roles]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Creating Roles: {str(e)}")


@router.get("/role/all",
            response_model=List[RoleResponse | RoleResponseWithUsers],
            status_code=status.HTTP_200_OK)
async def get_roles(db: db_dependency,
                    current_user: Annotated[dict, Depends(require_access_level(2))],
                    include_users: bool = True):
    """Get Roles details along with associated Users."""
    try:
        roles = db.query(Role).all()
        if include_users:
            return [RoleResponseWithUsers.model_validate(role) for role in roles]

        return [RoleResponse.model_validate(role) for role in roles]

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Error Fetching Role: {str(e)}")


@router.put("/role/mod/",
            response_model=List[RoleResponse],
            status_code=status.HTTP_202_ACCEPTED)
async def update_role(updated_data: List[RoleUpdateRequest], db: db_dependency,
                      current_user: Annotated[dict, Depends(require_access_level(5))]):
    """Update Existing Roles."""
    try:
        role_levels_to_update = {role.level: role for role in updated_data}
        roles = (
            db.query(Role)
            .filter(Role.level.in_(role_levels_to_update))
            .all()
        )

        for role in roles:
            updated_role = role_levels_to_update.get(role.level, None)
            if not updated_role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role Not Found for Level: {role.level}")

            role.role = updated_role.role

        db.commit()
        db.refresh(roles)

        return [RoleResponse.model_validate(role) for role in roles]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED,
                            detail=f"Error Updating Role: {str(e)}")


@router.delete("/role/del", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(roles_for_deletion: List[RoleDeleteRequest], db: db_dependency,
                      current_user: Annotated[dict, Depends(require_access_level(5))]):
    """Delete Roles."""
    try:
        role_levels_to_delete = [role.level for role in roles_for_deletion]
        roles_to_delete = (
            db.query(Role)
            .filter(Role.level.in_(role_levels_to_delete))
            .all()
        )
        if not roles_to_delete:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Roles Not Found")

        for role in roles_to_delete:
            db.delete(role)

        db.commit()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error Deleting Role: {str(e)}")
