import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import asyncio

#v1
from app.api.api_application import create_app
from app.api.router import routes
from app.models import CatalogoModel
from app.services import HealthCheckService, CatalogoServiceV1, CatalogoService
from app.settings import api_settings
from app.container import Container

#v2
from motor.motor_asyncio import AsyncIOMotorClient
from app.repositories.catalogo_repository import CatalogoRepository
from pytest import fixture
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from app.api.common.auth_handler import do_auth, get_current_user
from glob import glob

def refactor_fixture_path(string: str) -> str:
    return string.replace("/", ".").replace("\\", ".").replace(".py", "")

pytest_plugins = [
    refactor_fixture_path(fixture) for fixture in glob("tests/fixtures/**/*.py", recursive=True) if "__" not in fixture
]

# -------------------------------- FIXTURE PARA HEALTH CHECK--------------------
@pytest.fixture
def health_check_service(container: Container) -> HealthCheckService:
    return container.health_check_service()


# -------------------------------- FIXTURE PARA V1 --------------------
@pytest.fixture
def test_catalogo_v1() -> list[CatalogoModel]:
    return [
        CatalogoModel(
            seller_id="magalu2",
            sku="ma2cel",
            name="celular",


        ),
        CatalogoModel(
            seller_id="magalu3",
            sku="ma3notebook",
            name="notebook",


        ),
    ]

@pytest.fixture
def container_v1(test_catalogo_v1) -> Container:
    container = Container()
    container.config.from_pydantic(api_settings)
    repo = container.catalogo_repository_v1()
    # Popula o singleton do container!
    async def populate_repo(repo, produtos):
        for produto in produtos:
            await repo.create(produto)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(populate_repo(repo, test_catalogo_v1))
    loop.close()
    # Não sobrescreva o provider, pois já é singleton!
    container.catalogo_service_v1.override(CatalogoServiceV1(repo))
    return container

@pytest.fixture
def app_v1(container_v1: Container) -> FastAPI:
    import app.api.v1.routers.catalogo_seller_router as catalogo_seller_router_v1
    container_v1.wire(modules=[catalogo_seller_router_v1])
    app_instance = create_app(api_settings, routes)
    app_instance.container = container_v1  # type: ignore[attr-defined]
    yield app_instance
    container_v1.unwire()

@pytest.fixture
def client_v1(app_v1: FastAPI) -> TestClient:
    with TestClient(app_v1) as client:
        yield client

# --------------------------- FIXTURE PARA V2 -------------------------

"""
auth_fixture.py
clean_catalogo_fixture.py
"""
# --- FIXTURE DE MOCK PARA O REPOSITÓRIO DE CATÁLOGO ---
from unittest.mock import AsyncMock

#Acessar o banco diretamente
@pytest.fixture
def mongo_clientv2():
    return AsyncIOMotorClient("mongodb://admin:admin@localhost:27018/test_db?authSource=admin")




@pytest.fixture
def repository(mongo_clientv2):
    return CatalogoRepository(mongo_clientv2)

@pytest.fixture
def app_v2(mock_do_auth, container_v2: Container) -> FastAPI:
    import app.api.v2.routers.catalogo_seller_router as catalogo_seller_router_v2
    import app.api.common.auth_handler as auth_handler
    container_v2.wire(modules=[catalogo_seller_router_v2, auth_handler])
    app_instance = create_app(api_settings, routes)
    app_instance.container = container_v2  # type: ignore[attr-defined]
    yield app_instance
    container_v2.unwire()

@pytest.fixture
async def async_client(app_v2) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app_v2)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def client_v2(app_v2: FastAPI) -> TestClient:
    with TestClient(app_v2) as client:
        yield client