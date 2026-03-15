import string
import secrets
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from models import Base, User
from database import get_db
from main import app
from auth import hash_password


def generate_random_password(length=12):
    """Generate random password for test brittleness reduction"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_random_username(length=8):
    """Generate random username to avoid conflicts"""
    chars = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


@pytest.fixture(scope="function")
def test_db():
    """Create isolated in-memory SQLite database for each test"""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def test_client(test_db):
    """Provide FastAPI TestClient with test database"""

    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    yield client

    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_creds():
    """Generate random test credentials"""
    return {
        "username": generate_random_username(),
        "password": generate_random_password(),
    }


@pytest.fixture
def test_user(test_db, test_user_creds):
    """Create test user in database"""
    user = User(
        username=test_user_creds["username"],
        hashed_password=hash_password(test_user_creds["password"]),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(test_client, test_user_creds, test_user):
    """Provide TestClient with authenticated session"""
    # Simulate login to set session
    response = test_client.post("/login", data=test_user_creds)
    assert response.status_code in [200, 302]  # 302 = redirect after login
    return test_client
