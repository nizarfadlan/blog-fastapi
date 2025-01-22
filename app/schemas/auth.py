from typing import Optional

from pydantic import BaseModel

from .base import BaseResponse

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int
    exp: int
    is_refresh: Optional[bool] = False

class LoginResponse(BaseResponse[Token]):
    pass

class RefreshTokenResponse(BaseResponse[Token]):
    pass