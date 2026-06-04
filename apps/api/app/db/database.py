from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import require_database_url


class Base(DeclarativeBase):
    pass

_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def get_engine() -> Engine:
    global _engine

    if _engine is None:
        _engine = create_engine(
            require_database_url(),
            echo=False,
            pool_pre_ping=True,
        )

    return _engine


def get_session_factory() -> sessionmaker:
    global _session_factory

    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
        )

    return _session_factory

SessionLocal = get_session_factory()
