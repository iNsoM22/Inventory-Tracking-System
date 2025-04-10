from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import re
from schemas.user import User
from uuid import UUID
from datetime import timedelta, datetime, timezone
from sqlalchemy.orm import Session


load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("HASHING_ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


auth_form = Annotated[OAuth2PasswordRequestForm, Depends()]


def is_email(value: str) -> bool:
    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.fullmatch(email_pattern, value) is not None


def authenticate_user(username: str, password: str, db: Session) -> User | None:
    try:
        if is_email(username):
            user = db.query(User).filter(User.email == username).first()
        else:
            user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not bcrypt_context.verify(password, user.password):
            return None

        return user

    except Exception as e:
        return None


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


def require_access_level(min_level: int):
    def checker(user: user_dependency):
        if user["level"] < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient Privileges. Required level: {min_level}"
            )
        return user
    return checker


user_dependency = Annotated[dict, Depends(get_current_user)]
