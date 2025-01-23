from datetime import datetime, UTC

from slugify import slugify
from sqlalchemy import Column, Text, ForeignKey, VARCHAR, DateTime
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid_utils as uuid

from .base import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column("id", UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid7()))
    title = Column("title", VARCHAR(255), nullable=False)
    slug = Column("slug", VARCHAR(255), nullable=False, unique=True)
    content = Column("content", Text, nullable=False)
    thumbnail_file_id = Column("thumbnail_file_id", ForeignKey("files.id"), nullable=True)
    author_id = Column("author", ForeignKey("users.id"), nullable=False)

    created_at = Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column("updated_at", DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    deleted_at = Column("deleted_at", DateTime(timezone=True), default=None)

    author = relationship("User", backref="articles", foreign_keys=[author_id])
    thumbnail_file = relationship("File", backref="articles", foreign_keys=[thumbnail_file_id])

    def generate_slug(self, db: Session):
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Title must be a non-empty string.")

        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1

        while db.query(Article).filter(Article.slug == slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        return self.slug

    def soft_delete(self):
        self.deleted_at = datetime.now(UTC)

    def restore(self):
        self.deleted_at = None