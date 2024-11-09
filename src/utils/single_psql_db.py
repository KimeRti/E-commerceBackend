import contextlib

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import select, func

from src.settings import config

engine = create_async_engine(config.sql_uri, echo=True)
SessionLocal = async_sessionmaker(bind=engine)


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"

    @classmethod
    async def get_count(cls, where_query: Optional[str] = None):
        async with get_db() as db:
            if where_query is None:
                query = select(func.count()).select_from(cls)
            else:
                query = select(func.count()).select_from(cls).where(where_query)
            return await db.scalar(query)


@contextlib.asynccontextmanager
async def get_db() -> AsyncSession:
    db = SessionLocal()
    try:
        yield db
    except:
        await db.rollback()
        raise
    finally:
        await db.close()


async def init_psql_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("psql db created.")
