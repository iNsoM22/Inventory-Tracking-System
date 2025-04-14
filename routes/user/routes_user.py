from fastapi import APIRouter, status, HTTPException, Depends
from utils.db import db_dependency
from validations.user import (
    UserRequest,
    UserRead,
    UserPublicUpdateRequest,
    UserManagementUpdateRequest
)
from schemas.user import User
from utils.auth import (
    bcrypt_context,
    user_dependency,
    require_access_level
)
from typing import Annotated, List
from uuid import UUID
from sqlalchemy.future import select


router = APIRouter(prefix="/users")


@router.post("/public/add",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def create_public_user(user_data: UserRequest, db: db_dependency):
    """Add a New User with Access Level 1."""
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=bcrypt_context.hash(user_data.password),
            is_internal_user=user_data.is_internal_user
        )

        await db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserRead.model_validate(new_user)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Creating Public User: {str(e)}"
        )


@router.post("/management/add",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def create_internal_user(user_data: UserRequest,
                               db: db_dependency,
                               current_user: Annotated[dict, Depends(require_access_level(3))]):
    """Add a New User with Certain Access Levels (Internal Use Only)."""
    try:
        new_user = User(
            username=user_data.username,
            password=bcrypt_context.hash(user_data.password),
            email=user_data.email,
            is_internal_user=user_data.is_internal_user,
            level=user_data.level
        )

        if new_user.level >= current_user["level"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot Create a User with Equal or Higher Privileges."
            )

        await db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserRead.model_validate(new_user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Creating Internal User: {str(e)}"
        )


@router.get("/get/{identifier}",
            response_model=UserRead,
            status_code=status.HTTP_200_OK)
async def get_user_from_identifier(identifier: str | UUID,
                                   db: db_dependency,
                                   current_user: Annotated[dict, Depends(require_access_level(3))],
                                   from_username: bool = False,
                                   from_email: bool = False):
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )
        stmt = select(User)
        if from_username:
            stmt = stmt.where(User.username == identifier)
        elif from_email:
            stmt = stmt.where(User.email == identifier)
        else:
            stmt = stmt.where(User.id == identifier)
        
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )
        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error Fetching User: {str(e)}"
        )


@router.get("/all",
            response_model=List[UserRead],
            status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency,
                        current_user: Annotated[dict, Depends(require_access_level(4))],
                        limit: int = 50,
                        offset: int = 0):
    try:
        stmt = select(User).offset(offset).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return [UserRead.model_validate(user) for user in users]

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error Fetching Users Records: {str(e)}"
        )


@router.put("/mod",
            response_model=UserRead,
            status_code=status.HTTP_202_ACCEPTED)
async def modify_user(updated_user: UserPublicUpdateRequest,
                      db: db_dependency,
                      current_user: user_dependency):
    """Modify Details of the Current Authenticated User."""
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )

        stmt = select(User).where(User.id == current_user["id"])
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )

        if updated_user.new_username:
            user.username = updated_user.new_username
        if updated_user.new_password:
            user.password = bcrypt_context.hash(updated_user.new_password)
        if updated_user.new_email:
            user.email = updated_user.new_email

        await db.commit()
        await db.refresh(user)

        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error Modifying User: {str(e)}"
        )


@router.put("/management/mod/user",
            response_model=UserRead,
            status_code=status.HTTP_202_ACCEPTED)
async def modify_any_user(updated_user: UserManagementUpdateRequest,
                          db: db_dependency,
                          current_user: Annotated[dict, Depends(require_access_level(5))]):
    """Allow Admins to Modify Other Users Based on Access Level Hierarchy."""
    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )
        stmt = select(User)
        if updated_user.username:
            stmt = stmt.where(User.username == updated_user.username)
        elif updated_user.email:
            stmt = stmt.where(User.email == updated_user.email)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Username or Email Required")
            
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )

        if updated_user.new_level >= current_user["level"] or user.level >= current_user["level"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient Access Level to Modify This User."
            )

        if updated_user.new_username:
            user.username = updated_user.new_username
        if updated_user.new_password:
            user.password = bcrypt_context.hash(updated_user.new_password)
        if updated_user.new_email:
            user.email = updated_user.new_email
        if updated_user.new_level:
            user.level = updated_user.new_level

        await db.commit()
        await db.refresh(user)

        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error Modifying User: {str(e)}"
        )
