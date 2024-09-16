from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from typing import AsyncIterator
from typing_extensions import Annotated

from .settings import database_settings


async_engine: AsyncEngine = create_async_engine(
    database_settings.POSTGRES_CONN, echo=True
)


def get_async_sessionmaker():
    return sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async_sessionmaker = get_async_sessionmaker()


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_sessionmaker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
        else:
            await session.commit()


DatabaseSession = Annotated[AsyncSession, Depends(get_session)]
