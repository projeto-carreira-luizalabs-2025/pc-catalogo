from app.api.common.schemas import ResponseEntity, SchemaType


class SomethingSchema(SchemaType):
    seller_id: str
    sku: str
    product_name: str


class SomethingResponse(SomethingSchema, ResponseEntity):
    """Resposta adicionando"""


class SomethingCreate(SomethingSchema):
    seller_id: str
    sku: str
    product_name: str


class SomethingUpdate(SchemaType):
    """Permite apenas a atualização do nome do produto e do SKU"""
    seller_id: str
    sku: str
    product_name: str
