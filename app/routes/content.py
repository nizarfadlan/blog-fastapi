from typing import Optional

from fastapi import APIRouter, Depends, Form, File, UploadFile
import os

from app.core.security import get_current_user
from app.schemas.article import CreateArticleRequest
from app.schemas.user import User

router = APIRouter(prefix="/content", tags=["content"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_content():
    return {"message": "Get all content"}

@router.get("/{content_id}")
def get_content_by_id(content_id: int):
    return {"message": f"Get content with id {content_id}"}

@router.post("/", dependencies=[Depends(get_current_user)], response_model=CreateArticleRequest)
def create_content(
    title: str = Form(min_length=1, max_length=255),
    content: str = Form(min_length=1),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):

    return {"message": "Create content"}

@router.put("/{content_id}")
def update_content(content_id: int):
    return {"message": f"Update content with id {content_id}"}

@router.delete("/{content_id}")
def delete_content(content_id: int):
    return {"message": f"Delete content with id {content_id}"}