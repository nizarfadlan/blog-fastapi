from app.core.database import Session
from app.core.security import get_password_hash
from app.models import User, Role

users_data = [
    {
        "username": "admin",
        "name": "Admin User",
        "password": "admin123",
        "role_name": "admin"
    },
    {
        "username": "editor",
        "name": "Editor User",
        "password": "editor123",
        "role_name": "editor"
    },
]

def seed_users():
    db = Session()
    try:
        for user_data in users_data:
            role = db.query(Role).filter(Role.name == user_data["role_name"]).first()
            if not role:
                print(f"Role '{user_data['role_name']}' not found. Skipping user '{user_data['username']}'.")
                continue

            user = db.query(User).filter(User.username == user_data["username"]).first()
            if not user:
                hashed_password = get_password_hash(user_data["password"])
                user_data["password"] = hashed_password
                user_data["role_id"] = role.id

                del user_data["role_name"]

                db_user = User(**user_data)
                db.add(db_user)
                db.commit()
                print(f"User '{db_user.username}' created.")
            else:
                print(f"User '{user.username}' already exists.")
    finally:
        db.close()