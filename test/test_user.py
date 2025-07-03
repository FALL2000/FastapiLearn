from fastapi import Depends
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session
from config.db import Base
from models.users import User
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    user = User(name="John Doe", email="johndoe@example.com", nickname="johndoe")
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user.id, user 
    db.rollback()  
    db.close()

def test_create_user():
    response = client.post(
        "/adduser",
        json={"name":"dead pool","email": "deadpool@example.com", "nickname": "deadpool"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "deadpool@example.com"
    assert "id" in data

def test_get_users(test_user):
    user_id, user_data = test_user
    print(f"The name is {user_data.name} and id {user_id}.")
    response = client.get(f"/user/{user_data.name}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email"] == "johndoe@example.com"
    assert data["id"] == user_id
