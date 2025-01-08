import uuid
import os
from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport

from app.database.postgres.session import AsyncDatabaseSession, get_session
from app.main import app
from .constants import BASE_API_PREFIX


AUTH_API_PREFIX = f"{BASE_API_PREFIX}/auth"

@pytest.fixture(scope="session")
def config():
    return {
        "role_id": None,
        "menu_list": []
    }


@pytest.fixture(scope="session")
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope="session")
def postfix():
    return datetime.now().strftime("%Y%m%d%H%M%S")


# Use async db session
@pytest.fixture(scope="session")
async def test_db_session():
    async with AsyncDatabaseSession() as session:
        yield session


# Use AsyncClient to process
@pytest.fixture(scope="session")
async def base_client(test_db_session):
    def _get_db_override():
        return test_db_session

    app.dependency_overrides[get_session] = _get_db_override

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as c:
        yield c


@pytest.fixture(scope="session")
async def client(base_client):
    user = os.getenv("TEST_USER", "test@gmail.com")
    base_client.headers.update({"User": user})
    response = await base_client.get(f"{AUTH_API_PREFIX}/jwt/token")
    if response.status_code != 200 or 'jwt_token' not in response.json():
        pytest.exit(f"Failed to retrieve JWT token: {response.json()}")
    auth_token = response.json().get('jwt_token')
    print(f"User: {user}, Token: {auth_token}")
    base_client.headers.update({
        "User": user,
        "Authorization": f"{auth_token}"
    })

    yield base_client
