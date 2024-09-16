import pytest
from fastapi.testclient import TestClient
from backend.app_factory import create_app
from backend.database import SessionLocal, engine
from backend.models import Base


@pytest.fixture(scope="module")
def client():
    app = create_app()
    client = TestClient(app)
    yield client


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
