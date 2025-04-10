from fastapi import APIRouter, status, HTTPException, Depends
from utils.db import db_dependency
from validations.user import (
    Token,
    UserRequest,
    UserRead,
    UserPublicUpdateRequest,
    UserPublicResponse,
    UserManagementUpdateRequest
)
from schemas.user import User
from utils.auth import (
    bcrypt_context,
    auth_form,
    authenticate_user,
    create_access_token,
    user_dependency,
    require_access_level
)
from datetime import timedelta
from typing import Annotated, List


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/public/add",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def create_public_user(user_data: UserRequest, db: db_dependency):
    """Add a New User with Access Level 1."""
    try:
        new_user = User(
            username=user_data.username,
            password=bcrypt_context.hash(user_data.password),
            is_internal_user=user_data.is_internal_user
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

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
            is_internal_user=user_data.is_internal_user,
            level=user_data.level
        )

        if new_user.level >= current_user["level"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot Create a User with Equal or Higher Privileges."
            )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserRead.model_validate(new_user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error Creating Internal User: {str(e)}"
        )


@router.post("/login",
             response_model=Token,
             status_code=status.HTTP_202_ACCEPTED)
async def user_login(form_data: auth_form, db: db_dependency):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )

        token = create_access_token(
            user.username,
            user.id,
            expires_in=timedelta(minutes=30)
        )

        return Token(access_token=token, token_type="bearer")

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Login Failed: {str(e)}"
        )


@router.get("/get/user",
            response_model=UserRead,
            status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could Not Validate User"
            )

        return UserPublicResponse(
            id=user["id"],
            username=user["username"],
            level=user["level"],
            is_internal_user=user["is_internal_user"]
        )

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
        users = db.query(User).offset(offset).limit(limit).all()
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

        user = db.query(User).filter(User.username ==
                                     current_user["username"]).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Not Found"
            )

        if updated_user.new_username:
            user.username = updated_user.new_username
        if updated_user.new_password:
            user.password = bcrypt_context.hash(updated_user.new_password)

        db.commit()
        db.refresh(user)

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

        user = db.query(User).filter(User.username ==
                                     updated_user.username).first()

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
        if updated_user.new_level:
            user.level = updated_user.new_level

        db.commit()
        db.refresh(user)

        return UserRead.model_validate(user)

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error Modifying User: {str(e)}"
        )
