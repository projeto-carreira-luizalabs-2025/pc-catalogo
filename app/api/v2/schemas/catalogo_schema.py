from typing import Optional
from pydantic import Field

from app.api.common.schemas import ResponseEntity, SchemaType


class CatalogoSchema(SchemaType):
    seller_id: str = Field(..., pattern=r'^[a-z0-9]+$', description="Só letras minúsculas e números")
    sku: str = Field(..., pattern=r'^[A-Za-z0-9]+$', description="Só letras e números, sem espaços")
    name: str = Field(..., min_length=2, max_length=200, description="Nome entre 2 e 200 caracteres, sem só espaços")


class CatalogoResponse(CatalogoSchema, ResponseEntity):
    """Resposta adicionando"""


class CatalogoCreate(SchemaType):
    sku: str = Field(..., pattern=r'^[A-Za-z0-9]+$', description="Só letras e números, sem espaços")
    name: str = Field(..., min_length=2, max_length=200, description="Nome entre 2 e 200 caracteres, sem só espaços")


class CatalogoUpdate(SchemaType):
    """Permite apenas a atualização do nome do produto"""
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
        description="Nome do produto (opcional, mas não pode ser vazio se fornecido)"
    )
