from app.core.database import Session
from app.models import Article, User
from uuid_utils import uuid7
from datetime import datetime, UTC

articles_data = [
    {
        "title": "Pengenalan Python untuk Pemula",
        "content": "Python adalah bahasa pemrograman yang populer karena sintaksnya yang mudah dipahami...",
        "author_username": "admin",
        "thumbnail_file_id": None,
    },
    {
        "title": "Panduan Lengkap SQLAlchemy",
        "content": "SQLAlchemy adalah ORM (Object-Relational Mapping) yang powerful untuk Python...",
        "author_username": "editor",
        "thumbnail_file_id": None,
    }
]

def seed_articles():
    db = Session()
    try:
        for article_data in articles_data:
            author = db.query(User).filter(User.username == article_data["author_username"]).first()
            if not author:
                print(
                    f"Author with username '{article_data['author_username']}' not found. Skipping article '{article_data['title']}'.")
                continue

            article_data["id"] = str(uuid7())
            article_data["created_at"] = datetime.now(UTC)
            article_data["updated_at"] = datetime.now(UTC)
            article_data["deleted_at"] = None
            article_data["author_id"] = author.id

            del article_data["author_username"]

            article = Article(**article_data)
            article.slug = article.generate_slug()

            existing_article = db.query(Article).filter(Article.slug == article.slug).first()
            if not existing_article:
                db.add(article)
                db.commit()
                print(f"Article '{article.title}' created.")
            else:
                print(f"Article '{article.title}' already exists.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()