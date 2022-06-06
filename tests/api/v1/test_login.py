from httpx import AsyncClient

from app.core.config import settings


async def test_get_access_token(api_client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER_USERNAME,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = await api_client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )
    tokens = response.json()
    assert response.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
