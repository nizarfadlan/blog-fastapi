from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import InternalServerError, Ok, NotFound, BadRequest
from app.core.security import get_current_user, check_user_admin, get_password_hash, verify_password
from app.models import User
from app.schemas.base import BaseResponse
from app.schemas.user import ListUserResponse, DetailUser, DetailUserResponse, CreateUserRequest, UpdateUserRequest, \
    validate_username
import app.repository.user as user_repo

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", dependencies=[Depends(get_current_user)], response_model=ListUserResponse)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        users = user_repo.get_users(db)
        user_list = [DetailUser.model_validate(user).to_dict() for user in users]

        return Ok(data=user_list, message="Users retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.get("/{user_id}", dependencies=[Depends(get_current_user)], response_model=DetailUserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise NotFound(message="User not found").http_exception()

        return Ok(data=DetailUser.model_validate(user).to_dict(), message="User retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.post("/", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def create_user(
    req: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        hashed_password = get_password_hash(req.password)
        new_user = User(
            name=req.name,
            username=req.username,
            password=hashed_password,
            role_id=req.role,
        )

        user_repo.create_user(db, new_user)

        return Ok(message="User created successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.put("/{user_id}", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
async def update_user(
    user_id: int,
    req: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise NotFound(message="User not found").http_exception()
        if user.deleted_at:
            raise BadRequest(message="User is deleted").http_exception()

        validate_username(req.username, exclude_user_id=user_id)

        update_data = {}

        if req.name is not None:
            update_data["name"] = req.name
        if req.username is not None:
            update_data["username"] = req.username
        if req.role is not None:
            update_data["role_id"] = req.role
        if req.new_password is not None:
            if not req.old_password:
                raise BadRequest(message="Old password is required to change password.").http_exception()

            if not verify_password(req.old_password, user.password):
                raise BadRequest(message="Old password is incorrect.").http_exception()

            update_data["password"] = get_password_hash(req.new_password)

        if update_data:
            for key, value in update_data.items():
                setattr(user, key, value)
            user_repo.update_user(db, user)

        return Ok(message="User updated successfully").json()
    except ValueError as error:
        raise HTTPException(status_code=422, detail={"loc": ["body", "username"], "msg": str(error), "type": "value_error"})
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.patch("/{user_id}/restore", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def restore_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise NotFound(message="User not found").http_exception()

        user_repo.restore_user(db, user)

        return Ok(message="User restored successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.delete("/{user_id}", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise NotFound(message="User not found").http_exception()

        user_repo.soft_delete_user(db, user)

        return Ok(message="User deleted successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.delete("/{user_id}/permanently", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def delete_user_permanently(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            raise NotFound(message="User not found").http_exception()

        user_repo.delete_user(db, user)

        return Ok(message="User deleted permanently").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()