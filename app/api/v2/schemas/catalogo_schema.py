from typing import Optional
from pydantic import Field, validator

from app.api.common.schemas import ResponseEntity, SchemaType


class CatalogoSchema(SchemaType):
    seller_id: str = Field(..., pattern=r'^[a-z0-9]+$', description="Só letras minúsculas e números")
    sku: str = Field(..., pattern=r'^[A-Za-z0-9]+$', description="Só letras e números, sem espaços")
    name: str = Field(..., min_length=2, max_length=200, description="Nome entre 2 e 200 caracteres, sem só espaços")

    @validator("seller_id", pre=True)
    def clean_seller_id(cls, v):
        return v.replace(" ", "").lower().strip() if isinstance(v, str) else v

    @validator("sku", pre=True)
    def clean_sku(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("name", pre=True)
    def clean_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    
class CatalogoResponse(CatalogoSchema, ResponseEntity):
    """Resposta adicionando"""


class CatalogoCreate(CatalogoSchema):
    """Payload para criação."""


class CatalogoUpdate(SchemaType):
    """Permite apenas a atualização do nome do produto"""
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200,
        description="Nome do produto (opcional, mas não pode ser vazio se fornecido)"
    )

    @validator("name", pre=True)
    def clean_name(cls, v):
        return v.strip() if isinstance(v, str) else v