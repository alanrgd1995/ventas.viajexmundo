from pathlib import Path
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine


DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "viajexmundo.db"
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = "sqlite:///" + str(DATABASE_PATH)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)


def init_db() -> None:
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
