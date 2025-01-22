from typing import Optional, Sequence

from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from app.models import User

def get_user_by_id(
    db: Session,
    user_id: int,
) -> User:
    q = select(User).filter_by(id=user_id)
    return db.execute(q).scalar()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    query = select(User).filter(and_(User.username == username, User.deleted_at.is_(None)))
    return db.execute(query).scalar()

def get_users(db: Session) -> Sequence[User]:
    query = select(User).options(selectinload(User.role))
    return db.execute(query).scalars().all()

def create_user(db: Session, new_user: User) -> User:
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    return user

def soft_delete_user(db: Session, user: User) -> User:
    user.soft_delete()
    db.commit()
    db.refresh(user)
    return user

def restore_user(db: Session, user: User) -> User:
    user.restore()
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User) -> User:
    db.delete(user)
    db.commit()
    return user