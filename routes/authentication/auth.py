from fastapi import APIRouter, status, HTTPException
from utils.db import db_dependency
from validations.user import Token, UserRequest, UserRead, UserLoginRequest, UserPasswordUpdateRequest, UserPublicResponse
from schemas.user import User
from utils.auth import (
    bcrypt_context,
    auth_form,
    authenticate_user,
    create_access_token,
    user_dependency
)
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/add",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserRequest, db: db_dependency):
    try:
        new_user = User(username=user_data.username,
                        password=bcrypt_context.hash(user_data.password),
                        is_internal_user=user_data.is_internal_user)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserRead.model_validate(new_user)

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error Fetching Customer Records: {str(e)}")


@router.post("/login",
             response_model=Token,
             status_code=status.HTTP_202_ACCEPTED)
async def user_login(form_data: auth_form, db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could Not Validate User")

    token = create_access_token(user.username,
                                user.id,
                                expires_in=timedelta(minutes=30))

    return Token(access_token=token, token_type="bearer")


@router.get("/user", response_model=UserRead)
async def get_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could Not Validate User")
    return UserPublicResponse(
        id=user["id"],
        username=user["username"],
        level=user["level"],
        is_internal_user=user["is_internal_user"]
    )
