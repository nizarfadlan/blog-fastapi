from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role


def get_roles(db: Session) -> Sequence[Role]:
    query = select(Role)
    return db.execute(query).scalars().all()

def get_role_by_id(db: Session, role_id: int) -> Role:
    query = select(Role).filter_by(id=role_id)
    return db.execute(query).scalar()

def create_role(db: Session, new_role: Role) -> Role:
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

def update_role(db: Session, role: Role) -> Role:
    db.commit()
    db.refresh(role)
    return role

def is_role_exists(db: Session, role_name: str) -> bool:
    query = select(Role).filter_by(name=role_name)
    return db.execute(query).scalar() is not None

