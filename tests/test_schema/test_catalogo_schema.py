import pytest
from app.api.v2.schemas.catalogo_schema import CatalogoSchema

def test_catalogo_schema_normalizes_fields():
    data = {
        "seller_id": " MagAlu1 ",
        "sku": " SKU123 ",
        "name": "  Produto Teste  "
    }
    schema = CatalogoSchema(**data)
    assert schema.seller_id == "magalu1"
    assert schema.sku == "SKU123"
    assert schema.name == "Produto Teste"

def test_catalogo_schema_invalid_seller_id():
    with pytest.raises(Exception):
        CatalogoSchema(seller_id="MAGALU!", sku="SKU123", name="Produto Teste")