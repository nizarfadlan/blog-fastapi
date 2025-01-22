from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_token,
    get_user_from_token,
)
from app.models import User, Role

TEST_USER_ID = 1
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"
TEST_HASHED_PASSWORD = get_password_hash(TEST_PASSWORD)
TEST_SECRET_KEY = settings.SECRET_KEY
TEST_ALGORITHM = settings.ALGORITHM

# Mock Role
mock_role = Role(
    id=1,
    name="admin"
)

# Mock User
mock_user = User(
    id=TEST_USER_ID,
    username=TEST_USERNAME,
    password=TEST_HASHED_PASSWORD,
    role=mock_role
)

def test_verify_password():
    assert verify_password(TEST_PASSWORD, TEST_HASHED_PASSWORD) is True

    assert verify_password("wrongpassword", TEST_HASHED_PASSWORD) is False

def test_get_password_hash():
    hashed_password = get_password_hash(TEST_PASSWORD)
    assert isinstance(hashed_password, str)
    assert len(hashed_password) > 0

def test_create_token():
    access_token = create_token(mock_user)
    assert isinstance(access_token, str)

    refresh_token = create_token(mock_user, is_refresh=True)
    assert isinstance(refresh_token, str)

    expires_delta = timedelta(minutes=5)
    token_with_expiry = create_token(mock_user, expires_delta=expires_delta)
    payload = jwt.decode(token_with_expiry, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert "exp" in payload

@patch('app.core.security.get_user_by_id')
def test_get_current_user_valid_token(mock_get_user):
    valid_token = create_token(mock_user)

    mock_get_user.return_value = mock_user

    mock_db = MagicMock(spec=Session)
    user = get_user_from_token(mock_db, valid_token)

    assert user == mock_user
    assert user.id == TEST_USER_ID
    assert user.username == TEST_USERNAME

    mock_get_user.assert_called_once_with(mock_db, TEST_USER_ID)

@patch('app.core.security.get_user_by_id')
def test_get_current_user_invalid_token(mock_get_user):
    invalid_token = "invalid.token.string"

    mock_db = MagicMock(spec=Session)

    with pytest.raises(HTTPException) as exc_info:
        get_user_from_token(mock_db, invalid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {"status": "error", "message": "Could not validate credentials"}

    mock_get_user.assert_not_called()

@patch('app.core.security.get_user_by_id')
def test_get_current_user_user_not_found(mock_get_user):
    valid_token = create_token(mock_user)

    mock_get_user.return_value = None

    mock_db = MagicMock(spec=Session)

    with pytest.raises(HTTPException) as exc_info:
        get_user_from_token(mock_db, valid_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {"status": "error", "message": "Could not validate credentials"}

    mock_get_user.assert_called_once_with(mock_db, TEST_USER_ID)