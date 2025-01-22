from app.core.database import Session
from app.models.role import Role

roles_data = [
    {"name": "admin"},
    {"name": "editor"},
]

def seed_roles():
    db = Session()
    try:
        for role_data in roles_data:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                db_role = Role(**role_data)
                db.add(db_role)
                db.commit()
                print(f"Role '{db_role.name}' created.")
            else:
                print(f"Role '{role.name}' already exists.")
    finally:
        db.close()