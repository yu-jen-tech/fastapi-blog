from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# 1. Connection URL: 3 slashes + ./ means relative path in current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# 2. Engine interface
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },  # SQLite-specific: allows multi-threaded requests
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Declarative Base class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass


# Dependency Injection generator for FastAPI routes
def get_db() -> Generator[Session]:
    with SessionLocal() as db:
        yield db
