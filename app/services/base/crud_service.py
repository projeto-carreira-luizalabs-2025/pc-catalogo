from typing import Any, Generic, TypeVar

from app.api.common.schemas import Paginator
from app.models.base import PersistableEntity
from app.repositories import AsyncCrudRepository

T = TypeVar("T", bound=PersistableEntity)
ID = TypeVar("ID")

class CrudService(Generic[T, ID]):
    def __init__(self, repository: AsyncCrudRepository[T, ID]):
        self.repository = repository

    @property
    def context(self):
        return None

    @property
    def author(self):
        # XXX Pegar depois
        return None

    async def create(self, entity: Any) -> T:
        return await self.repository.create(entity)

    """async def find_by_id(self, entity_id: ID) -> T | None:
        return await self.repository.find_by_id(entity_id)
    
    async def find_by_sku(self, sku: str) -> T | None:
        return await self.repository.find_by_sku(sku)"""
    
    async def find_product(self, seller_id: str,sku: str) -> T | None:
        return await self.repository.find_product(seller_id, sku)
    
    """async def find_by_product_name(self, paginator: Paginator, filters: dict) -> list[T]:
        return await self.repository.find_by_product_name(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order())"""
    
    async def find(self, paginator: Paginator, filters: dict) -> list[T]:
        return await self.repository.find(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order())
        
    async def find_by_seller_id(self, seller_id: str) -> T | None:
        return await self.repository.find_by_seller_id(seller_id)
    
    async def find_by_filter(self, seller_id: str, paginator: Paginator = None, name_like: str = None) -> list[T]:
        return await self.repository.find_by_seller_id2(seller_id)

    """    async def delete_by_sellerid_sku(self, seller_id, sku) -> bool:
        return await self.repository.delete_by_sellerid_sku(seller_id, sku)

    async def find_by_id(self, entity_id: ID) -> T | None:
        return await self.repository.find_by_id(entity_id)
    
    async def find_by_product_name(self, filters: dict, paginator: Paginator) -> list[T]:
        return await self.repository.find_by_product_name(
            filters=filters, limit=paginator.limit, offset=paginator.offset, sort=paginator.get_sort_order())"""
    
    async def find_by_sku(self, sku: str) -> T | None:
        return await self.repository.find_by_sku(sku)

    async def patch(self, entity_id: ID, entity: Any) -> T:
        return await self.repository.update(entity_id, entity)

    async def delete_by_id(self, entity_id: ID) -> None:
        await self.repository.delete_by_id(entity_id)

    async def delete(self, product) -> None:
        await self.repository.delete(product)
