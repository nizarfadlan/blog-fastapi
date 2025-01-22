from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as SQLAlchemyAsyncSession
from sqlalchemy.orm import (
    sessionmaker, scoped_session,
)
from .config import settings

DATABASE_URI = settings.POSTGRES_URI
DATABASE_SYNC_PREFIX = settings.POSTGRES_SYNC_PREFIX
DATABASE_ASYNC_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_SYNC_PREFIX}{DATABASE_URI}"
DATABASE_ASYNC_URL = f"{DATABASE_ASYNC_PREFIX}{DATABASE_URI}"

engine = create_engine(
    DATABASE_URL,
    pool_size=100,
    max_overflow=0,
    pool_timeout=300,
)
Session = sessionmaker(engine, future=True)
factory_session = scoped_session(Session)

async_engine = create_async_engine(DATABASE_ASYNC_URL, echo=False, future=True)
AsyncSession = sessionmaker(bind=async_engine, class_=SQLAlchemyAsyncSession, expire_on_commit=False)

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSession() as db:
        try:
            yield db
        finally:
            await db.close()