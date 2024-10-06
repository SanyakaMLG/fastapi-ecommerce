from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Generator, Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from datetime import datetime, UTC


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Establish a connection to the PostgreSQL database
engine = create_async_engine(DATABASE_URL, echo='debug')

created_at = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


# Create database tables based on the defined SQLAlchemy models (subclasses of the Base class)
class Base(DeclarativeBase):
    created_at: Mapped[created_at]


# Connect to the database and provide a session for interacting with it
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session