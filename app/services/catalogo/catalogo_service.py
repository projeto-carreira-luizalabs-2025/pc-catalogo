from app.api.common.schemas.pagination import Paginator
from ...models import CatalogoModel
from ...repositories import CatalogoRepository
from ..base import CrudService
from .catalogo_exceptions import ( 
    NoFieldsToUpdateException, 
    ProductAlreadyExistsException, 
    ProductNotExistException,
    ProductNameLengthException,
    SellerIDException, 
    SKULengthException, 
    SellerIDNotExistException, 
    LikeNotFoundException
)

from app.api.v1.schemas.catalogo_schema import CatalogoUpdate
from typing import TypeVar

T = TypeVar("T")

class CatalogoService(CrudService[CatalogoModel, int]):
    def __init__(self, repository: CatalogoRepository):
        super().__init__(repository)


    async def create(self, catalogo: CatalogoModel) -> CatalogoModel:
        """
        Cria um novo produto no catálogo.
        """
        await self.review(catalogo)
        await self.validate(catalogo)
        return await self.save(catalogo)

    async def validate(self, catalogo: CatalogoModel) -> None:
        
        await self.validate_len_seller_id(catalogo.seller_id)
        await self.validate_len_sku(catalogo.sku)
        await self.validate_len_product_name(catalogo.name)
        await self.validate_product_exist(catalogo.seller_id, catalogo.sku)

    async def review(self, catalogo: CatalogoModel) -> None:
        # Converte e limpa campos
        catalogo.seller_id = catalogo.seller_id.lower().strip()
        catalogo.sku = catalogo.sku.strip()
        catalogo.name = catalogo.name.strip()

    async def save(self, catalogo: CatalogoModel) -> CatalogoModel:
        return await super().create(catalogo)
    
    async def update_by_sellerid_sku(self, seller_id: str, sku: str, model: T) -> T:
        model = await self.validate_update(seller_id, sku, model)
        model = await self.repository.update_by_sellerid_sku(seller_id, sku, model)
        return model
    
    async def delete_by_sellerid_sku(self, seller_id: str, sku: str, raises_exception: bool = True) -> bool:
        """ 
        Deleta um produto do catálogo com base no seller_id e SKU.
        """
        await self.validate_delete(seller_id, sku)
        deleted = await self.repository.delete_by_sellerid_sku(seller_id, sku)
        return deleted
    
    async def patch_by_sellerid_sku(self, seller_id: str, sku: str, patch_model: dict) -> T:
        await self.find_by_seller_id(seller_id)
        patch_model = await self.validate_patch(seller_id, sku, patch_model)
        model = await self.repository.patch_by_sellerid_sku(seller_id, sku, patch_model)
        return model
    
    async def find_by_filter(self, seller_id: str, paginator: Paginator = None, name_like: str = None) -> list[CatalogoModel]:
        """ 
        Busca produtos no catálogo filtrando por seller_id e opcionalmente por nome (like).
        """
        filters = {"seller_id": seller_id.lower()}
        if name_like:
            filters["name"] = {"$regex": name_like, "$options": "i"}
        limit = paginator.limit if paginator else 50
        offset = paginator.offset if paginator else 0
        sort = paginator.get_sort_order() if paginator else None
        result = await self.repository.find(filters=filters, limit=limit, offset=offset, sort=sort)
        if not result:
            if name_like:
                raise LikeNotFoundException()
            else:
                raise SellerIDNotExistException()
        return result

    async def validate_product_exist(self, seller_id: str, sku: str) -> None:
        """
        Valida se um produto pode ser criado verificando se já existe um produto com o mesmo seller_id e SKU.
        """
        try:
            # Tenta encontrar o produto pelo seller_id e SKU
            product_exist = await self.find_product(seller_id, sku)
        except Exception:  # Captura NotFoundException ou equivalente
            product_exist = None

        # Se o produto já existir, lança uma exceção
        if product_exist:
            raise ProductAlreadyExistsException()
        
    async def validate_len_product_name(self, name: str) -> None:
        """
        Valida o tamanho do nome do produto.
        """
        if not name or name.strip() == "" or not (2 <= len(name.strip()) <= 200):
            raise ProductNameLengthException()

    async def validate_len_sku(self, sku: str) -> None:
        """
        Valida o SKU.
        """
        if not isinstance(sku, str) or not sku.strip() or len(sku.strip()) < 2:
        
            raise SKULengthException()
        
    async def validate_len_seller_id(self, seller_id: str) -> None:
        """
        Valida o seller_id.
        """
        if not isinstance(seller_id, str) or not seller_id.strip() or len(seller_id.strip()) < 2:
            raise SellerIDException()

    async def validate_patch(self, seller_id, sku, patch_model) -> dict:

        try:
            product_exist = await self.find_product(seller_id, sku)
        except Exception:
            product_exist = None

        if not product_exist:
            raise ProductNotExistException()

        return patch_model
    
    async def validate_update(self, seller_id: str, sku: str, catalogo: CatalogoModel) -> CatalogoModel:
        try:
            product_exist = await self.find_product(seller_id, sku)
        except Exception:
            product_exist = None

        if not product_exist:
            raise ProductNotExistException()

        return catalogo
            
    async def validate_delete(self, seller_id: str, sku: str):
        try:
            product_exist = await self.find_product(seller_id, sku)
        except Exception:
            product_exist = None

        if not product_exist:
            raise ProductNotExistException()
        
    async def find_by_sellerid_sku(self, seller_id: str, sku: str, raises_exception: bool = True) -> T | None:
        try:
            product_exist = await self.repository.find_by_sellerid_sku(seller_id, sku)
        except Exception:
            product_exist = None

        if not product_exist:
            if raises_exception:
                raise ProductNotExistException()
            return None
        return product_exist


   