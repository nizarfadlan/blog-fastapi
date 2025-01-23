import pytest
from fastapi.testclient import TestClient

from app.core.security import get_password_hash
from app.main import app
from app.models import Article, User, Role
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

def test_create_content(db, user):
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.post(
        "/content/",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "title": "Test Title",
            "content": "Test Content"
        },
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article created successfully"

def test_get_content(db, user):
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get("/content/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Articles retrieved successfully"

def test_update_content(db, user):
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    create_response = client.post(
        "/content/",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "Test Title", "content": "Test Content"},
    )
    content_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/content/{content_id}",
        headers={"Authorization": f"Bearer {token}"},
        data={"title": "Updated Title", "content": "Updated Content"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article updated successfully"

def test_delete_content(db, user):
    login_response = client.post(
        "/login",
        json={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    create_response = client.post(
        "/content/",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "title": "Test Title",
            "content": "Test Content"
        },
    )
    content_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/content/{content_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article deleted successfully"