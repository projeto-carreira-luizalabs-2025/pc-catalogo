from typing import Type, Generic, List, Optional, TypeVar

from uuid import UUID
from pymongo import ReturnDocument

from pydantic import BaseModel

from app.common.datetime import utcnow
from app.integrations.database.mongo_client import MongoClient
from app.models import PersistableEntity, QueryModel

from app.common.exceptions import NotFoundException

from .async_crud_repository import AsyncCrudRepository

T = TypeVar("T", bound=BaseModel)
ID = TypeVar("ID", bound=int | str)
Q = TypeVar("Q", bound=QueryModel)


class MongoCatalogoRepository(AsyncCrudRepository[T, ID], Generic[T, ID]):

    def __init__(self, client: MongoClient, collection_name: str, model_class: Type[T]):
        """
        Repositório genérico para MongoDB.

        :param client: Instância do MongoClient.
        :param collection_name: Nome da coleção.
        :param model_class: Classe do modelo (usada para criar instâncias de saída).
        """
        self.collection = client.get_default_database()[collection_name]
        self.model_class = model_class

    async def create(self, entity: T) -> T:
        entity_dict = entity.model_dump(by_alias=True)
        when = utcnow()
        entity_dict["created_at"] = when
        entity_dict["updated_at"] = when

        created = await self.collection.insert_one(entity_dict)
        # XXX Rever pegar chave do banco.
        entity_dict["_id"] = created.inserted_id
        return self.model_class(**entity_dict)
    

#Busca pelo ID
    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        result = next((r for r in self.memory if r.seller == entity_id), None)
        return result
    
# Busca pelo seller_id no repositório em memória
    async def find_by_seller_id(self, seller_id: str) -> Optional[T]:
        result = [r for r in self.memory if r.seller_id == seller_id]
        return result
    
# Busca pelo seller_id no repositório em memória
    async def find_by_seller_id2(self, seller_id: str) -> Optional[T]:
        result = [r for r in self.memory if r.seller_id == seller_id]
        return result
    
# Busca pelo SKU no repositório em memória
    async def find_by_sku(self, sku: str) -> Optional[T]:
        result = next((r for r in self.memory if r.sku == sku), None)
        return result
    
# Busca por um produto unico seller + sku
    async def find_product(self, id: str, sku: str) -> Optional[T]:
        id = id.lower()
        result = next((r for r in self.memory if r.sku == sku and r.seller_id == id), None)
        return result
    
# Busca por um produto ou mais produtos pelo seller + product_name paginados
    async def find_by_product_name(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:
        seller_id = filters.get("seller_id")
        name = filters.get("name")
        
        filtered_list = [
            item for item in self.memory
            if (seller_id is None or item.seller_id.lower() == seller_id.lower())
            and (name is None or item.name.lower() == name.lower())
        ]

        return filtered_list[offset:offset + limit]

#Deleta um produto do repositório em memória
    async def delete(self, product) -> None:
        if product in self.memory:
            result = self.memory.remove(product)
            return result
        else:
            return None

    async def update(self, entity_id: ID, entity_update_payload) -> T:
        index_toupdate = -1
        found_entity = None
        for i, item in enumerate(self.memory):
            if hasattr(item, "seller_id") and item.seller_id == entity_id:
                index_to_update = i
                found_entity = item
                break
            elif hasattr(item, 'id') and item.id == entity_id:
                index_to_update = i
                found_entity = item
                break
        if found_entity is None:
            return None
        
        update_data = entity_update_payload.model_dump(exclude_unset=True)
        
        if not update_data:
            return found_entity
        
        for key, value in update_data.items():
            if hasattr(found_entity, key):
                setattr(found_entity, key, value)
            
        if hasattr(found_entity, "updated_at"):
            setattr(found_entity, "updated_at", utcnow())
            
        return found_entity

    async def delete_by_id(self, entity_id: ID) -> None:
        # XXX TODO
        current_document = await self.find_by_id(entity_id)
        if not current_document:
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
       
        
    async def find2(self, filters: dict, limit: int = 10, offset: int = 0, sort: Optional[dict] = None) -> List[T]:
        def matches_filters(item):
            for key, value in filters.items():
                attr = getattr(item, key, None)
                if attr is None:
                    return False
                # Case-insensitive comparison for strings
                if isinstance(attr, str) and isinstance(value, str):
                    if attr.lower() != value.lower():
                        return False
                else:
                    if attr != value:
                        return False
            return True

        filtered_list = [data for data in self.memory if matches_filters(data)]

        # Optional sorting
        if sort:
            for key, direction in reversed(sort.items()):
                reverse = direction.lower() == "desc"
                filtered_list.sort(key=lambda x: getattr(x, key, None), reverse=reverse)

        return filtered_list[offset:offset + limit]
