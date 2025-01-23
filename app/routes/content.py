from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
import os

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import InternalServerError, Ok, NotFound, BadRequest
from app.core.security import get_current_user
from app.models import Article, File as FileModel
from app.schemas.article import ListArticleResponse, DetailArticleResponse, CreateArticleResponse
from app.schemas.base import BaseResponse
from app.schemas.user import User
import app.repository.file as file_repo
import app.repository.article as article_repo

router = APIRouter(prefix="/content", tags=["content"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_FILE_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE = 5 * 1024 * 1024

def save_uploaded_file(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise BadRequest(message="File type not allowed. Only JPEG and PNG are allowed.").http_exception()

    if file.size > MAX_FILE_SIZE:
        raise BadRequest(message=f"File size exceeds the maximum limit of {MAX_FILE_SIZE // (1024 * 1024)} MB.").http_exception()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_ext = file.filename.split(".")[-1]
    filename = f"{timestamp}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path

def delete_uploaded_file(file_path: str):
    os.remove(file_path)

@router.get("/", dependencies=[Depends(get_current_user)], response_model=ListArticleResponse)
def get_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        articles = article_repo.get_articles(db, current_user.id)

        return Ok(data=articles, message="Articles retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.get("/{content_id}", dependencies=[Depends(get_current_user)], response_model=DetailArticleResponse)
def get_content_by_id(
    content_id: str,
    db: Session = Depends(get_db)
):
    try:
        article = article_repo.get_article_by_id(db, content_id)

        if not article:
            return NotFound(message="Article not found").http_exception()

        return Ok(data=article, message="Article retrieved successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.post("/", dependencies=[Depends(get_current_user)], response_model=CreateArticleResponse)
def create_content(
    title: str = Form(min_length=1, max_length=255),
    content: str = Form(min_length=1),
    thumbnail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    thumbnail_file = None
    file_path = None
    try:
        if thumbnail:
            try:
                file_path = save_uploaded_file(thumbnail)

                new_file = FileModel(file_path=file_path)
                thumbnail_file = file_repo.create_file(db, new_file)
            except HTTPException as error:
                db.rollback()
                if file_path:
                    delete_uploaded_file(file_path)

                raise error
            except Exception:
                db.rollback()
                if file_path:
                    delete_uploaded_file(file_path)

                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Failed to save the uploaded file.")

        new_article = Article(
            title=title,
            content=content,
            thumbnail_file_id=thumbnail_file.id if thumbnail_file else None,
            author_id=current_user.id
        )
        new_article.slug = new_article.generate_slug(db)
        article = article_repo.create_article(db, new_article)

        db.commit()
        return Ok(data={"id": str(article.id)}, message="Article created successfully").json()
    except HTTPException as error:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        raise error
    except Exception:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.put("/{content_id}", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def update_content(
    content_id: str,
    title: Optional[str] = Form(None, min_length=1, max_length=255),
    content: Optional[str] = Form(None, min_length=1),
    thumbnail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_path = None
    try:
        article = article_repo.get_article_by_id_db(db, content_id)

        if not article:
            return NotFound(message="Article not found").http_exception()
        if article.deleted_at:
            return BadRequest(message="Article is already deleted").http_exception()
        if article.author.id != current_user.id:
            return BadRequest(message="You are not allowed to update this content").http_exception()

        old_thumbnail: FileModel | None = None
        if thumbnail:
            try:
                file_path = save_uploaded_file(thumbnail)
                new_file = FileModel(file_path=file_path)
                thumbnail_file = file_repo.create_file(db, new_file)

                if article.thumbnail_file:
                    old_thumbnail = article.thumbnail_file

                article.thumbnail_file_id = thumbnail_file.id
            except HTTPException as error:
                db.rollback()
                if file_path:
                    delete_uploaded_file(file_path)
                raise error
            except Exception:
                db.rollback()
                if file_path:
                    delete_uploaded_file(file_path)
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Failed to save the uploaded file.")

        if title is not None:
            article.title = title
            article.slug = article.generate_slug(db)
        if content is not None:
            article.content = content

        article_repo.update_article(db, article)
        if old_thumbnail:
            delete_uploaded_file(old_thumbnail.file_path)
            file_repo.delete_file(db, old_thumbnail)

        db.commit()
        return Ok(message="Article updated successfully").json()
    except HTTPException as error:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        raise error
    except Exception:
        db.rollback()
        if file_path:
            delete_uploaded_file(file_path)

        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.patch("/{content_id}/restore", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def restore_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        article = article_repo.get_article_by_id_db(db, content_id)

        if not article:
            return NotFound(message="Article not found").http_exception()

        if article.author.id != current_user.id:
            return BadRequest(message="You are not allowed to restore this content").http_exception()

        article_repo.restore_article(db, article)

        db.commit()
        return Ok(message="Article restored successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.delete("/{content_id}", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        article = article_repo.get_article_by_id_db(db, content_id)

        if not article:
            return NotFound(message="Article not found").http_exception()

        if article.author.id != current_user.id:
            return BadRequest(message="You are not allowed to delete this content").http_exception()

        article_repo.soft_delete_article(db, article)

        db.commit()
        return Ok(message="Article deleted successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()

@router.delete("/{content_id}/permanently", dependencies=[Depends(get_current_user)], response_model=BaseResponse)
def delete_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        article = article_repo.get_article_by_id_db(db, content_id)

        if not article:
            return NotFound(message="Article not found").http_exception()

        if article.author.id != current_user.id:
            return BadRequest(message="You are not allowed to delete this content").http_exception()

        article_repo.delete_article(db, article)
        if article.thumbnail_file:
            file_repo.delete_file(db, article.thumbnail_file)
            delete_uploaded_file(article.thumbnail.file_path)

        db.commit()
        return Ok(message="Article deleted successfully").json()
    except HTTPException as error:
        raise error
    except Exception:
        import traceback
        traceback.print_exc()
        return InternalServerError(error="Internal Server Error").http_exception()