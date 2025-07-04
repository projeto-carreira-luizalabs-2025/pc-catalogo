from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")
Q = TypeVar("Q")



class AsyncCrudRepository(ABC, Generic[T, ID]):
    """
    Interface genérica para operações de repositório CRUD.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Salva uma entidade no repositório.
        """

    @abstractmethod
    async def find_product(self, id: str ,sku: str) -> T | None:
        """
        Busca uma entidade pelo seu id+sku.
        """

    @abstractmethod
    async def find(self, filters: Q, limit: int = 20, offset: int = 0, sort: dict | None = None) -> list[T]:
        """
        Busca entidades no repositório, utilizando filtros e paginação.
        """

    @abstractmethod
    async def update(self, entity_id: ID, entity: Any) -> T:
        """
        Atualiza uma entidade existente no repositório.
        """

    @abstractmethod
    async def delete(self, product) -> None:
        """
        Remove uma entidade pelo seu identificador único.
        """