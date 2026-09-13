from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.infra.models import Base

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "hanse.db"
DB_PATH = Path(os.getenv("HANSE_DB_PATH", DEFAULT_DB_PATH))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, future=True, connect_args={"timeout": 30})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    inspector = inspect(engine)
    if inspector.has_table("game_sessions"):
        raise RuntimeError(
            "Diese Datenbank gehört zum Vorgänger. Bitte einen neuen Datenpfad nutzen."
        )
    if inspector.has_table("game_snapshots"):
        columns = {c["name"] for c in inspector.get_columns("game_snapshots")}
        required = {"id", "name", "payload_json", "checksum", "game_date", "updated_at"}
        if not required.issubset(columns):
            raise RuntimeError("Unbekanntes Speicherformat. Die Datenbank bleibt unverändert.")
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
