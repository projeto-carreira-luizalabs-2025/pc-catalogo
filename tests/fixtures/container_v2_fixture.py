import pytest
from app.services import CatalogoService
from app.repositories.catalogo_repository import CatalogoRepository
from app.container import Container
from app.settings import api_settings
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock

@pytest.fixture
def container_v2(mongo_clientv2) -> Container:
    container = Container()
    container.config.from_pydantic(api_settings)
    repo = CatalogoRepository(mongo_clientv2)
    container.catalogo_repository.override(repo)
    container.catalogo_service.override(CatalogoService(repo))

    # Mock do keycloak_adapter
    fake_adapter = AsyncMock()
    fake_adapter.validate_token.return_value = {
        "sub": "fake-user-id",
        "iss": "fake-issuer",
        "sellers": "magalu11"
    }
    container.keycloak_adapter.override(fake_adapter)
    return container
