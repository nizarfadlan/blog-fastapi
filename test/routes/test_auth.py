import pytest
from fastapi.testclient import TestClient

from app.core.database import Session, clear_all_data_on_database
from app.core.security import get_password_hash
from app.main import app
from app.models import User, Role
from app.models.base import Base
from app.core.database import engine

client = TestClient(app)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        clear_all_data_on_database(db)

@pytest.fixture
def role(db: Session):
    role = Role(name="admin")
    db.add(role)
    db.commit()
    return role

@pytest.fixture
def user(db: Session, role: Role):
    user = User(
        username="testuser",
        password=get_password_hash("testpassword"),
        name="Test User",
        role_id=role.id
    )
    db.add(user)
    db.commit()
    return user

def test_login_successful(db: Session, user: User):
    response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

def test_login_invalid_credentials(db: Session):
    response = client.post(
        "/login",
        json={
            "username": "invaliduser",
            "password": "invalidpassword"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Invalid credentials"

def test_token_successful(db: Session, user: User):
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "testpassword"
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"

def test_token_invalid_username(db: Session):
    response = client.post(
        "/token",
        data={
            "username": "invaliduser",
            "password": "testpassword"
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Invalid credentials"

def test_token_invalid_password(db: Session, user: User):
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"]["message"] == "Invalid credentials"

def test_refresh_token(db: Session, user: User):
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    refresh_token = login_response.cookies.get("refresh_token")

    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/refresh")

    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

def test_refresh_token_missing():
    client.cookies.clear()
    response = client.post("/refresh")

    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"]["message"] == "Refresh token missing."

def test_logout():
    response = client.post("/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"