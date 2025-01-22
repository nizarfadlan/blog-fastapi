from datetime import datetime, UTC

from sqlalchemy import Column, Integer, VARCHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    username = Column("username", VARCHAR(20), nullable=False, unique=True)
    name = Column("name", VARCHAR(100), nullable=False)
    password = Column("password", VARCHAR(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    created_at = Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(UTC))
    deleted_at = Column("deleted_at", DateTime(timezone=True), default=None)

    role = relationship("Role", backref="users", foreign_keys=[role_id])

    def soft_delete(self):
        self.deleted_at = datetime.now(UTC)

    def restore(self):
        self.deleted_at = None
