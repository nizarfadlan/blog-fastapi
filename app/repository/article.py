from typing import List
import os

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models import Article
from app.schemas.article import DetailArticle, DetailAuthor


def get_articles(db: Session, author_id: str) -> List[DetailArticle]:
    articles = (
        db.query(Article)
        .options(joinedload(Article.thumbnail_file), joinedload(Article.author))
        .filter_by(author_id=author_id)
        .all()
    )

    return [
        DetailArticle(
            id=str(article.id),
            title=article.title,
            content=article.content,
            thumbnail_url=f"/static/{os.path.basename(article.thumbnail_file.file_path)}" if article.thumbnail_file else None,
            created_at=article.created_at,
            updated_at=article.updated_at,
            deleted_at=article.deleted_at,
            author=DetailAuthor(id=article.author.id, name=article.author.name)
        ).to_dict()
        for article in articles
    ]

def get_article_by_id_db(db: Session, article_id: str) -> Article | None:
    article = (
        db.query(Article)
        .options(joinedload(Article.thumbnail_file), joinedload(Article.author))
        .filter(Article.id == article_id)
        .first()
    )

    return article

def get_article_by_id(db: Session, article_id: str) -> DetailArticle | None:
    article = (
        db.query(Article)
        .options(joinedload(Article.thumbnail_file), joinedload(Article.author))
        .filter(and_(Article.deleted_at.is_(None), Article.id == article_id))
        .first()
    )

    if not article:
        return None

    return DetailArticle(
        id=str(article.id),
        title=article.title,
        content=article.content,
        thumbnail_url=f"/static/{os.path.basename(article.thumbnail_file.file_path)}" if article.thumbnail_file else None,
        created_at=article.created_at,
        updated_at=article.updated_at,
        deleted_at=article.deleted_at,
        author=DetailAuthor(id=article.author.id, name=article.author.name)
    ).to_dict()

def create_article(db: Session, new_article: Article) -> Article:
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

def update_article(db: Session, article: Article):
    db.commit()
    db.refresh(article)

def soft_delete_article(db: Session, article: Article):
    article.soft_delete()
    db.commit()
    db.refresh(article)

def restore_article(db: Session, article: Article):
    article.restore()
    db.commit()
    db.refresh(article)

def delete_article(db: Session, article: Article):
    db.delete(article)
    db.commit()