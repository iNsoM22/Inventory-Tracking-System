from fastapi import APIRouter, status, HTTPException
from utils.db import db_dependency
from validations.user import (
    Token,
    UserRead,
    UserPublicResponse,
)
from utils.auth import (
    auth_form,
    authenticate_user,
    create_access_token,
    user_dependency,
)
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/me",
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
