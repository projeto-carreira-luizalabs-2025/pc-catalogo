from pydantic import Field
from .base import SelllerSkuUuidPersistableEntity


class CatalogoModel(SelllerSkuUuidPersistableEntity):
    seller_id: str = Field(..., pattern=r'^[a-z0-9]+$', description="Só letras minúsculas e números")
    sku: str = Field(..., pattern=r'^[A-Za-z0-9]+$', description="Só letras e números, sem espaços")
    name: str = Field(..., min_length=2, max_length=200, description="Nome entre 2 e 200 caracteres, sem só espaços")

