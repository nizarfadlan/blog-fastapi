from datetime import datetime
from typing import Optional, Annotated, List

from fastapi import UploadFile
from pydantic import BaseModel, StringConstraints

from app.schemas.base import BaseResponse


class CreateArticleRequest(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    content: Annotated[str, StringConstraints(min_length=1)]
    thumbnail: Optional[UploadFile] = None

class UpdateArticleRequest(BaseModel):
    title: Optional[Annotated[str, StringConstraints(min_length=1, max_length=255)]]
    content: Optional[Annotated[str, StringConstraints(min_length=1)]]
    thumbnail: Optional[UploadFile] = None

class DetailAuthor(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class DetailArticle(BaseModel):
    id: str
    title: str
    content: str
    thumbnail_file: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    author: DetailAuthor

    class Config:
        from_attributes = True

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'thumbnail_file': self.thumbnail_file,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'author': self.author.to_dict() if self.author else None
        }

class DetailArticleResponse(BaseResponse[DetailArticle]):
    pass

class ListArticleResponse(BaseResponse[List[DetailArticle]]):
    pass