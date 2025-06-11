from datetime import datetime
from uuid import UUID as UuidType

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from app.common.datetime import utcnow


class IdModel(BaseModel):
    id: UuidType | int | None = Field(None, description="Chave")


class UuidModel(IdModel):
    id: UuidType | None = Field(None, alias="_id")


class IntModel(IdModel):
    id: int | None = Field(None, description="Identificador")


class AuditModel(BaseModel):
    created_at: datetime | None = Field(default_factory=utcnow, description="Data e hora da criação")
    updated_at: datetime | None = Field(None, description="Data e hora da atualização")


class PersistableEntity(IdModel, AuditModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    @classmethod
    def from_json(cls, json_data: str):
        return TypeAdapter(cls).validate_json(json_data)


class UuidPersistableEntity(PersistableEntity, UuidModel):
    """
    Entidade cuja chave é um uuid
    """


class IntPersistableEntity(PersistableEntity, IntModel):
    """
    Entidiade cuja chave é um inteiro.
    """


class SellerSkuEntity(BaseModel):
    seller_id: str = Field(..., description="ID do seller")
    sku: str = Field(..., description="ID do produto")

    def get_sellerid_sku(self) -> dict:
        return {"seller_id": self.seller_id, "sku": self.sku}


class SelllerSkuUuidPersistableEntity(SellerSkuEntity, UuidPersistableEntity):
    """
    Entidade com seller_id e sku e chave uuid.
    """


class SelllerSkuIntPersistableEntity(SellerSkuEntity, IntPersistableEntity):
    """
    Entidade com seller_id e sku e chave int.
    """

