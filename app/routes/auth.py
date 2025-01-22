from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.response import InternalServerError, BadRequest, Ok, Unauthorized
from app.core.security import verify_password, create_token, get_user_from_token
from app.repository.user import get_user_by_username
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenResponse

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest = Depends(), db: Session = Depends(get_db)):
    try:
        user = get_user_by_username(db=db, username=req.username)

        if not user:
            raise BadRequest(message="Invalid credentials").http_exception()

        if not verify_password(req.password, user.password):
            raise BadRequest(message="Invalid credentials").http_exception()

        access_token = create_token(user=user)
        refresh_token = create_token(user=user, is_refresh=True)
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        response = Ok(
            message="Login successful",
            data={"access_token": access_token, "token_type": "Bearer"}
        ).json()
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
        )

        return response
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()


@router.post("/token")
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = get_user_by_username(db=db, username=form_data.username)

        if not user:
            raise BadRequest(message="Invalid credentials").http_exception()

        if not verify_password(form_data.password, user.password):
            raise BadRequest(message="Invalid credentials").http_exception()

        access_token = create_token(user=user)

        return {"access_token": access_token, "token_type": "Bearer"}
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh(request: Request, db: Session = Depends(get_db)):
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise Unauthorized(message="Refresh token missing.").http_exception()

        user = get_user_from_token(db, refresh_token, is_refresh=True)

        access_token = create_token(user=user)
        refresh_token = create_token(user=user, is_refresh=True)
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        response = Ok(
            message="Token refreshed",
            data={"access_token": access_token, "token_type": "Bearer"}
        ).json()
        response.set_cookie(
            key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="Lax", max_age=max_age
        )

        return response
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()


@router.post("/logout")
def logout(request: Request):
    response = Ok(message="Logout successful").json()
    response.delete_cookie(key="refresh_token")

    return response