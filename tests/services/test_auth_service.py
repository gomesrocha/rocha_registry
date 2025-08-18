import pytest
from unittest.mock import MagicMock
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user,
)
from app.models.user import User
from jose import jwt
import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-for-testing")
ALGORITHM = "HS256"

def test_verify_password():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == "testuser"

@pytest.mark.anyio
async def test_get_current_user():
    mock_session = MagicMock()
    mock_user = User(username="testuser", hashed_password="hashedpassword")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    token_data = {"sub": "testuser"}
    token = create_access_token(token_data)

    user = await get_current_user(token=token, session=mock_session)
    assert user.username == "testuser"

@pytest.mark.anyio
async def test_get_current_active_user():
    mock_user = User(username="testuser", hashed_password="hashedpassword", disabled=False)
    user = await get_current_active_user(mock_user)
    assert user.username == "testuser"

@pytest.mark.anyio
async def test_get_current_active_user_disabled():
    mock_user = User(username="testuser", hashed_password="hashedpassword", disabled=True)
    with pytest.raises(Exception):
        await get_current_active_user(mock_user)
