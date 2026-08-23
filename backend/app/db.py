"""
SQLite engine + session. Offline by design — no network calls in this module,
matching the "offline at every tier" requirement in the architecture doc.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

DB_PATH = os.getenv("CIVICVERIFY_DB_PATH", "civicverify.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables if they don't exist yet. Safe to call on every boot."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
