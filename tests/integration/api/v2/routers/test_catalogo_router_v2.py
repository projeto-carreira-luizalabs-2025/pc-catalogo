import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient



#@pytest.mark.usefixtures("client_v2") OLD
@pytest.mark.usefixtures("mock_do_auth", "async_client")
class TestCatalogoRouterV2:

    @pytest.mark.asyncio    
    async def test_criar_produto(self, async_client: AsyncClient):
        novo_produto = {"x-seller-id": "magalu11", "sku": "magalu10", "name": "20"}
        resposta = await async_client.post(
            "/seller/v2/catalogo",
            json=novo_produto,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
            }
        )
        assert resposta.status_code == 201
        assert resposta.json()["seller_id"] == "magalu11"
        assert resposta.json()["sku"] == "magalu10"
        assert resposta.json()["name"] == "20"


    @pytest.mark.asyncio
    async def test_buscar_produto_sellerid_sku(self, async_client: AsyncClient):
        novo_produto = {"x-seller-id": "magalu11", "sku": "magalu10", "name": "20"}
        resposta = await async_client.post(
            "/seller/v2/catalogo",
            json=novo_produto,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
            }
        )
        assert resposta.status_code == 201
        # Busca o produto via API
        resposta = await async_client.get(
            "/seller/v2/catalogo/magalu10",
            headers={
            "x-seller-id": "magalu11",
            "Authorization": "Bearer fake-token"})
        assert resposta.status_code == 200
        data = resposta.json()
        assert data["seller_id"] == "magalu11"
        assert data["sku"] == "magalu10"

    @pytest.mark.asyncio
    async def test_deletar_catalogo(self, async_client: AsyncClient):
        # Cria o produto via API
        novo_produto = {"x-seller-id": "magalu11", "sku": "magalu10", "name": "20"}
        resposta = await async_client.post(
            "/seller/v2/catalogo",
            json=novo_produto,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
            }
        )
        assert resposta.status_code == 201
        # Deleta o produto
        resposta = await async_client.delete(
            "/seller/v2/catalogo/magalu10",
            headers={
            "x-seller-id": "magalu11",
            "Authorization": "Bearer fake-token"})
        assert resposta.status_code == 204

    async def test_atualizar_catalogo(self, async_client: AsyncClient):
        # Cria o produto via API
        novo_produto = {"x-seller-id": "magalu11", "sku": "magalu10", "name": "tv20"}
        resposta = await async_client.post(
            "/seller/v2/catalogo",
            json=novo_produto,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
            }
        )
        assert resposta.status_code == 201

        # Atualiza o produto
        update = {"name": "tv50"}
        resposta = await async_client.put(
            "/seller/v2/catalogo/magalu10",
            json=update,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
                }
            )
        assert resposta.status_code == 202
        assert resposta.json()["name"] == "tv50"

    async def test_patch_catalogo(self, async_client: AsyncClient):
        # Cria o produto via API
        novo_produto = {"x-seller-id": "magalu11", "sku": "magalu10", "name": "tv20"}
        resposta = await async_client.post(
            "/seller/v2/catalogo",
            json=novo_produto,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
            }
        )
        assert resposta.status_code == 201

        # Atualiza o produto
        update = {"name": "tv50"}
        resposta = await async_client.patch(
            "/seller/v2/catalogo/magalu10",
            json=update,
            headers={
                "x-seller-id": "magalu11",
                "Authorization": "Bearer fake-token"
                }
            )
        assert resposta.status_code == 202
        assert resposta.json()["name"] == "tv50"
