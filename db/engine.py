from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..settings import DB_CONN


class Base(DeclarativeBase):
    pass

engine = create_async_engine(
    DB_CONN,
    isolation_level = "READ COMMITTED"
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def async_session_context():
    connection = async_session_maker()
    try:
        yield connection
    except Exception as error:
        await connection.rollback()
        raise error
    else:
        await connection.commit()
    finally:
        await connection.close()
