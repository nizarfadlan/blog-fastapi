from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import File

def get_file_by_id(db: Session, file_id: int) -> File:
    query = select(File).filter_by(id=file_id)
    return db.execute(query).scalar()

def create_file(db: Session, new_file: File) -> File:
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def delete_file(db: Session, file: File):
    db.delete(file)
    db.commit()