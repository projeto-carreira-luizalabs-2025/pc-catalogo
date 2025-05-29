import pytest
from unittest.mock import AsyncMock

from app.services.catalogo.catalogo_service import CatalogoService
from app.models.catalogo_model import Catalogo

@pytest.mark.asyncio
async def test_create_catalogo_success():
    mock_repo = AsyncMock()
    service = CatalogoService(repository=mock_repo)
    catalogo = Catalogo(seller_id="magalu", sku="sku1", name="Produto")

    mock_repo.find_product.return_value = None
    mock_repo.create.return_value = catalogo

    result = await service.create(catalogo)
    assert result == catalogo
    mock_repo.create.assert_awaited_once_with(catalogo)

@pytest.mark.asyncio
async def test_create_catalogo_already_exists():
    mock_repo = AsyncMock()
    service = CatalogoService(repository=mock_repo)
    catalogo = Catalogo(seller_id="magalu", sku="sku1", name="Produto")

    mock_repo.find_product.return_value = catalogo

    with pytest.raises(Exception):  # Troque pelo exception correto se quiser
        await service.create(catalogo)