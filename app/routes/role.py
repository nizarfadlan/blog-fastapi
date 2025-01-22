from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import InternalServerError, Ok, BadRequest, NotFound
from app.core.security import get_current_user, check_user_admin
from app.models import User, Role
import app.repository.role as role_repo
from app.schemas.base import BaseResponse
from app.schemas.role import CreateRoleRequest, ListRoleResponse, DetailRoleResponse, UpdateRoleRequest, DetailRole

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("/", dependencies=[Depends(get_current_user)], response_model=ListRoleResponse)
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        roles = role_repo.get_roles(db)
        role_list = [DetailRole.model_validate(role).to_dict() for role in roles]

        return Ok(data=role_list, message="Roles retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception as error:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.get("/{role_id}", dependencies=[Depends(get_current_user)], response_model=DetailRoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        role = role_repo.get_role_by_id(db, role_id)
        if not role:
            raise NotFound(message="Role not found").http_exception()

        return Ok(data=role, message="Role retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception as error:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.post("/", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def create_role(
    req: CreateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        is_role_name_exists = role_repo.is_role_exists(db, req.name)
        if is_role_name_exists:
            raise BadRequest(message="Role name already exists").http_exception()

        new_role = Role(
            name=req.name
        )

        role_repo.create_role(db, new_role)

        return Ok(message="Role created successfully").json()
    except HTTPException as error:
        raise error
    except Exception as error:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.put("/{role_id}", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def update_role(
    role_id: int,
    req: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        check_user_admin(current_user)

        role = role_repo.get_role_by_id(db, role_id)
        if not role:
            raise NotFound(message="Role not found").http_exception()

        if role.name != req.name:
            is_role_name_exists = role_repo.is_role_exists(db, req.name)
            if is_role_name_exists:
                raise BadRequest(message="Role name already exists").http_exception()

        role.name = req.name
        role_repo.update_role(db, role)

        return Ok(message="Role updated successfully").json()
    except HTTPException as error:
        raise error
    except Exception as error:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()