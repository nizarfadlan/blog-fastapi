from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, StringConstraints, field_validator, ConfigDict
from typing_extensions import Annotated

from app.core.database import factory_session
from app.models import User, Role
from .role import DetailRole
from .base import BaseResponse

def validate_role(role_id: int) -> int:
    if not role_id:
        raise ValueError("Role must not be empty.")
    with factory_session() as session:
        existing_role = session.query(Role).filter_by(id=role_id).first()
        if not existing_role:
            raise ValueError("Role does not exist.")
    return role_id

def validate_password(password: str) -> str:
    if not password:
        raise ValueError("Password must not be empty.")
    elif len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    elif not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit.")
    elif not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    elif not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    elif not any(not char.isalnum() for char in password):
        raise ValueError("Password must contain at least one special character.")
    return password

def validate_username(username: str, exclude_user_id: Optional[int] = None) -> str:
    if not username:
        raise ValueError("Username must not be empty.")
    with factory_session() as session:
        query = session.query(User).filter(User.username == username)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        existing_username = query.first()
        if existing_username:
            raise ValueError("Username is already taken.")
    return username

class BaseUserRequest(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    username: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    password: Annotated[str, StringConstraints(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$")]
    role: int

class CreateUserRequest(BaseUserRequest):
    @field_validator("role")
    def validate_role(cls, value):
        return validate_role(value)

    @field_validator("password")
    def validate_password(cls, value):
        return validate_password(value)

    @field_validator("username")
    def validate_username(cls, value):
        return validate_username(value)

class UpdateUserRequest(BaseModel):
    name: Optional[Annotated[str, StringConstraints(min_length=1, max_length=100)]] = None
    username: Optional[Annotated[str, StringConstraints(min_length=1, max_length=20)]] = None
    old_password: Optional[str] = None
    new_password: Optional[
        Annotated[str, StringConstraints(pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$")]] = None
    role: Optional[int] = None

    @field_validator("role")
    def validate_role(cls, value):
        if value is not None:
            return validate_role(value)
        return value

    @field_validator("new_password")
    def validate_new_password(cls, value, values):
        if value is not None:
            if not values.data.get("old_password"):
                raise ValueError("Old password is required.")
            return validate_password(value)
        return value

class DetailUser(BaseModel):
    id: int
    name: str
    username: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    role: DetailRole

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'role': self.role.to_dict() if self.role else None
        }

class DetailUserResponse(BaseResponse[DetailUser]):
    pass

class ListUserResponse(BaseResponse[List[DetailUser]]):
    pass
