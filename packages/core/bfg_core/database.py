from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def create_engine_and_session(database_url: str, debug: bool = False):
    """Create async engine and session factory. Called by each product's main.py."""
    engine = create_async_engine(database_url, echo=debug)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, session_factory
