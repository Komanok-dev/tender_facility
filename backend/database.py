from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import project_settings
from .models import Base

engine = create_engine(project_settings.POSTGRES_CONN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
