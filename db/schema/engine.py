from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine(
    DB_COIN,
    isolation_level = "READ COMMITED"
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
