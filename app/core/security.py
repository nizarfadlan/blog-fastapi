from datetime import timedelta, datetime, UTC
from typing import Optional

from fastapi import Depends
from jwt import InvalidTokenError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.response import Unauthorized, Forbidden
from app.models import User
from app.repository.user import get_user_by_id
from app.schemas.auth import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(user: User, expires_delta: Optional[timedelta] = None, is_refresh: bool = False) -> str:
    if expires_delta:
        expire = datetime.now(tz=UTC) + expires_delta
    else:
        expire = datetime.now(tz=UTC) + (
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            if is_refresh
            else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {
        "user_id": user.id,
        "exp": expire
    }

    if is_refresh:
        to_encode["is_refresh"] = True

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_and_decode_jwt(token: str, is_refresh: bool = False) -> dict:
    credentials_exception = Unauthorized(message="Could not validate credentials")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp, tz=UTC) < datetime.now(tz=UTC):
            raise credentials_exception.http_exception()

        if is_refresh and not payload.get("is_refresh"):
            raise Unauthorized(message="Invalid token type").http_exception()

        return payload

    except InvalidTokenError:
        raise credentials_exception.http_exception()


def get_user_from_token(db: Session, token: str, is_refresh: bool = False) -> User:
    credentials_exception = Unauthorized(message="Could not validate credentials")

    try:
        payload = verify_and_decode_jwt(token, is_refresh)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception.http_exception()

        token_data = TokenData(user_id=user_id, exp=payload.get("exp"), is_refresh=payload.get("is_refresh"))

    except InvalidTokenError as error:
        raise error

    user = get_user_by_id(db, token_data.user_id)
    if user is None:
        raise credentials_exception.http_exception()
    return user

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    return get_user_from_token(db, token)

def check_user_admin(user: User):
    if not user.role.name == "admin":
        raise Forbidden().http_exception()