from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from schemas.user import User
from uuid import UUID
from datetime import timedelta, datetime, timezone


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("HASHING_ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


auth_form = Annotated[OAuth2PasswordRequestForm, Depends()]


def authenticate_user(username: str, password: str, db) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return

    if not bcrypt_context.verify(password, user.password):
        return

    return user


def create_access_token(username: str, user_id: UUID, is_internal_user: bool,
                        level: int, expires_in: timedelta) -> str:
    encode = {
        "sub": username,
        "id": user_id,
        "acc": level,
        "intuser": is_internal_user
    }
    expires = datetime.now(timezone.utc) + expires_in
    encode["exp"] = expires
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        level: int = payload.get("acc")
        is_internal_user: bool = payload.get("intuser")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user."
            )

        return {
            "username": username,
            "id": user_id,
            "level": level,
            "is_internal_user": is_internal_user
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user."
        )


user_dependency = Annotated[dict, Depends(get_current_user)]

# Add User Level Details in the Token (done)
# Create Function to Decode the Token and Get Current User Details (done)
# Add Level Based Access Points
