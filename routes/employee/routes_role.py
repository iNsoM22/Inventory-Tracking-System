from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from validations.employee import (RoleRequest, 
                                  RoleResponse, 
                                  RoleResponseWithEmployees, 
                                  RoleUpdateRequest,
                                  RoleDeleteRequest)
from utils.db import db_dependency 
from schemas.employee import Role


router = APIRouter(prefix="/management")


@router.post("/role/add", response_model=List[RoleResponse])
async def create_role(roles: List[RoleRequest], db: db_dependency):
    """Create a New Role."""
    try:
        new_roles = [Role(**role.model_dump()) for role in roles]
        db.add_all(new_roles)
        db.commit()
        
        return RoleResponse.model_validate(new_roles)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Creating Roles: {str(e)}")


@router.get("/role/all", response_model=List[RoleResponseWithEmployees | RoleResponse])
async def get_roles(db: db_dependency, include_employees: bool = True):
    """Get Roles details along with associated employees."""
    try:
        roles = db.query(Role).all()    
        if include_employees:
            return [RoleResponseWithEmployees.model_validate(role) for role in roles]
        
        return [RoleResponse.model_validate(role) for role in roles]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Fetching Role: {str(e)}")


@router.put("/role/mod/", response_model=List[RoleResponse])
async def update_role(updated_data: List[RoleUpdateRequest], db: db_dependency):
    """Update Existing Roles."""
    try:
        role_levels_to_update = {role.level:role for role in updated_data}
        roles = db.query(Role).filter(Role.level.in_(role_levels_to_update.keys())).all()
        
        for role in roles:
            updated_role = role_levels_to_update.get(role.level, None)
            if not updated_role:
                raise HTTPException(status_code=404, detail=f"Role Not Found for Level: {role.level}")
            role.role = updated_role.role
            
        db.commit()
        db.refresh(roles)
        
        return [RoleResponse.model_validate(role) for role in roles]
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Updating Role: {str(e)}")


@router.delete("/role/del", status_code=204)
async def delete_role(roles_for_deletion: List[RoleDeleteRequest], db: db_dependency):
    """Delete Roles."""
    try:
        role_levels_to_delete = [role.level for role in roles_for_deletion]
        roles_to_delete = db.query(Role).filter(Role.level.in_(role_levels_to_delete)).all()
        
        if not roles_to_delete:
            raise HTTPException(status_code=404, detail="Roles Not Found")

        for role in roles_to_delete:
            db.delete(role)
            
        db.commit()
        return {"detail": "Role Deleted Successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Deleting Role: {str(e)}")