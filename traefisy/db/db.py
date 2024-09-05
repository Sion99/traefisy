import typer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# SQLite 데이터베이스 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'traefisy.db')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스 생성
Base = declarative_base()


def check_if_db_exists():
    if os.path.exists(os.path.join(BASE_DIR, 'traefisy.db')):
        if typer.confirm("An existing database was found. Do you want to clear it and start fresh?", default=True):
            os.remove(os.path.join(BASE_DIR, 'traefisy.db'))
            typer.echo("Existing database has been deleted.")
            return True
        else:
            typer.echo("Keeping the existing database.")
            return False
    else:
        return True


def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
