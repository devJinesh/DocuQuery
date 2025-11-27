"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import settings
from models import Base

# SQLite database URL
DATABASE_URL = f"sqlite:///{settings.database_path}"
ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{settings.database_path}"

# Create sync engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.debug
)

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.debug
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db() -> Session:
    """Get synchronous database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
