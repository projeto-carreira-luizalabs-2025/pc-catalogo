from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.common.datetime import utcnow
from app.common.exceptions import NotFoundException

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=int | str)


class AsyncMemoryRepository(AsyncCrudRepository[T, ID], Generic[T, ID]):

    def __init__(self):
        super().__init__()
        self.memory = []
        # Deveria passar dinamco

    async def create(self, entity: T) -> T:
        entity_dict = entity.model_dump(by_alias=True)
        entity_dict["created_at"] = utcnow()

        self.memory.append(entity)

        return entity_dict

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        #Busca pelo ID do seller

        result = next((r for r in self.memory if r.seller_id == entity_id), None)
        if result:
            return result

        raise NotFoundException()
    
    async def find_by_sku(self, sku: str) -> Optional[T]:
        # Busca pelo SKU no repositório em memória
        result = next((r for r in self.memory if r.sku == sku), None)
        if result:
            return result
        raise NotFoundException()

    async def find_product(self, id: str, sku: str) -> Optional[T]:
        # Busca por um produto unico seller + sku
        result = next((r for r in self.memory if r.sku == sku and r.seller_id == id), None)
        if result:
            return result
        raise NotFoundException("Produto não encontrado.")
    
    async def update(self, entity_id: ID, entity: Any) -> T:
        # Busca o produto pelo seller_id e sku
        product = await self.find_product(entity.seller_id, entity.sku)

        if product:

            # Atualiza o campo product_name
            if hasattr(entity, "product_name"): 
                product.product_name = entity.product_name

            # Atualiza o campo updated_at
            if hasattr(product, "updated_at"):
                product.updated_at = utcnow()
            return product

        raise NotFoundException()
    
    
    async def delete_product(self, product) -> None:

        if product in self.memory:
            self.memory.remove(product)
            return {"message": "Product deleted successfully"}
        
        raise NotFoundException()
    
    async def find(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:

        filtered_list = [
            data
            for data in self.memory
                
            # TODO Criar filtro
        ]

        # XXX TODO Falta ordenar    

        entities = []
        for document in filtered_list:
            entities.append(document)
        return entities



    async def delete_by_id(self, entity_id: ID) -> None:
        # XXX TODO
        current_document = await self.find_by_id(entity_id)
        if not current_document:
            raise NotFoundException()
        

        
        
