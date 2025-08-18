from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_session
from app.models.user import User

client = TestClient(app)

def test_register_user_success():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None  # Simulate user not existing

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.post("/v2/register", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    app.dependency_overrides = {}

def test_register_user_already_exists():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = User(username="testuser", hashed_password="somepassword")

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.post("/v2/register", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

    app.dependency_overrides = {}

@patch('app.api.auth.verify_password', return_value=True)
def test_login_success(mock_verify_password):
    mock_user = User(username="testuser", hashed_password="hashedpassword")
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = mock_user

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.post("/v2/token", data={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    app.dependency_overrides = {}

def test_login_invalid_credentials():
    mock_session = MagicMock()
    mock_session.exec.return_value.first.return_value = None

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.post("/v2/token", data={"username": "wronguser", "password": "wrongpassword"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

    app.dependency_overrides = {}
