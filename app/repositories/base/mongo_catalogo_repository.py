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
    
    @staticmethod
    def build_sellerid_sku_filter(seller_id: str, sku: str) -> dict:
        filter = {"seller_id": seller_id, "sku": sku}
        return filter
    
    @staticmethod
    def build_sellerid_filter(seller_id: str) -> dict:
        filter = {"seller_id": seller_id}
        return filter
    
    # Busca por um produto unico seller + sku
    async def find_product(self, id: str, sku: str) -> Optional[T]:
        id = id.lower()
        filter = self.build_sellerid_sku_filter(id, sku)
        result = await self.find_one(filter)
        return result

    async def find_one(self, filter: dict) -> T | None:
        result = await self.collection.find_one(filter)
        if result is not None:
            result = self.model_class(**result)
        return result
    
    async def find(self, filters: dict, limit: int = 20, offset: int = 0, sort: dict | None = None) -> List[T]:
        query = filters  # agora é um dict
        cursor = self.collection.find(query)
        if sort:
            for field, order in sort.items():
                cursor = cursor.sort(field, order)
        cursor = cursor.skip(offset).limit(limit + 1)

        entities = []
        async for document in cursor:
            entities.append(self.model_class(**document))
        return entities

    async def _update_document(self, filter: dict, document: dict) -> T | None:
        document["updated_at"] = utcnow()

        updated_document = await self.collection.find_one_and_update(
            filter,
            {"$set": document},
            return_document=ReturnDocument.AFTER,
        )
        if updated_document:
            updated_document = self.model_class(**updated_document)
        return updated_document

    async def update(self, filter: dict, entity: T) -> T | None:
        entity_dict = entity.model_dump(by_alias=True, exclude={"id"})

        updated_document = await self._update_document(filter, entity_dict)
        return updated_document

    async def update_by_sellerid_sku(self, seller_id, sku, entity: T) -> T | None:
        filter = self.build_sellerid_sku_filter(seller_id, sku)

        updated_document = await self.update(filter, entity)
        return updated_document

    async def patch_by_sellerid_sku(self, seller_id, sku, patch_entity) -> T | None:

        filter = self.build_sellerid_sku_filter(seller_id, sku)
        updated_document = await self._update_document(filter, patch_entity)
        return updated_document
    
    async def find_by_sellerid_sku(self, seller_id: str, sku: str) -> T | None:
        filter = self.build_sellerid_sku_filter(seller_id, sku)
        result = await self.find_one(filter)
        return result

    async def find_by_seller_id(self, seller_id: str) -> T | None:
        filter = self.build_sellerid_filter(seller_id)
        result = await self.find_one(filter)
        return result
    
    async def delete(self, filter: dict) -> bool:
        # XXX Atenção aqui!
        deleted = await self.collection.delete_many(filter)
        has_deleted = deleted.deleted_count > 0
        return has_deleted

    async def delete_by_sellerid_sku(self, seller_id, sku) -> bool:
        filter = self.build_sellerid_sku_filter(seller_id, sku)
        has_deleted = await self.delete(filter)
        return has_deleted

