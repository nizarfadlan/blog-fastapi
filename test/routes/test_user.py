import pytest
from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.main import app
from app.models import User, Role
from app.models.base import Base
from app.core.database import Session, clear_all_data_on_database, engine

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
def role_admin(db: Session):
    role = Role(name="admin")
    db.add(role)
    db.commit()
    return role

@pytest.fixture
def role_editor(db: Session):
    role = Role(name="editor")
    db.add(role)
    db.commit()
    return role

@pytest.fixture
def user_admin(db: Session, role_admin: Role):
    user = User(
        username="testuser",
        password=get_password_hash("testpassword"),
        name="Test User",
        role_id=role_admin.id
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture
def user_editor(db: Session, role_editor: Role):
    user = User(
        username="editoruser",
        password=get_password_hash("editorpassword"),
        name="Editor User",
        role_id=role_editor.id
    )
    db.add(user)
    db.commit()
    return user

def test_forbidden_access(db, user_editor):
    login_response = client.post("/login", json={"username": "editoruser", "password": "editorpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"]["message"] == "Forbidden"

def test_create_user(db, user_admin, role_editor):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New User", "username": "newuser", "password": "@New12345", "role": role_editor.id},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"

def test_create_user_invalid_password(db, user_admin, role_editor):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New User", "username": "newuser", "password": "@Ni12", "role": role_editor.id},
    )
    assert response.status_code == 422
    assert response.json()["errors"][0]["ctx"]["error"] == "Password must be at least 8 characters long."

def test_create_user_invalid_role(db, user_admin):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New User", "username": "newuser", "password": "@New12345", "role": 100},
    )
    assert response.status_code == 422
    assert response.json()["errors"][0]["ctx"]["error"] == "Role does not exist."

def test_get_users(db, user_admin):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Users retrieved successfully"

def test_update_user(db, user_admin, role_editor):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    create_response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New User", "username": "newuser", "password": "@New12345", "role": role_editor.id},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated User", "username": "updateduser", "role": role_editor.id},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User updated successfully"

def test_delete_user(db, user_admin, role_editor):
    login_response = client.post("/login", json={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    create_response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New User", "username": "newuser", "password": "@New12345", "role": role_editor.id},
    )
    user_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"