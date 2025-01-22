from sqlalchemy import Column, Integer, VARCHAR

from .base import Base

class File(Base):
    __tablename__ = "files"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    file_path = Column("file_path", VARCHAR(255), nullable=False)