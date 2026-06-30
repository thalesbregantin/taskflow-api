from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

connect_args: dict[str, object] = {}
if settings.DATABASE_SSL:
    # Supabase pooler (transaction mode) requires SSL and no prepared statements
    connect_args = {"ssl": True, "statement_cache_size": 0}
engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool, connect_args=connect_args)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
