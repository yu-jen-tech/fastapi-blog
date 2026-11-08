from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Connection URL: 3 slashes + ./ means relative path in current directory
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

# Engine interface
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Declarative Base class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass


# Dependency Injection generator for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
