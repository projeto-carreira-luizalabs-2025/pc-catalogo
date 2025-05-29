from app.api.common.schemas.pagination import Paginator
from ...models import Catalogo
from ...repositories import CatalogoRepository
from ..base import CrudService
from fastapi import HTTPException
from .catalogo_exceptions import NoFieldsToUpdateException, ProductAlreadyExistsException, ProductNotExistException,ProductNameLengthException,SellerIDException, SKULengthException, SellerIDNotExistException, LikeNotFoundException
from app.api.v1.schemas.catalogo_schema import CatalogoUpdate

class CatalogoService(CrudService[Catalogo, int]):
    def __init__(self, repository: CatalogoRepository):
        super().__init__(repository)


    async def create(self, catalogo: Catalogo) -> Catalogo:
        """
        Cria um novo produto no catálogo.
        """
        await self.validate(catalogo)
        return await self.save(catalogo)

    async def validate(self, catalogo: Catalogo) -> None:

        await self.validade_len_seller_id(catalogo.seller_id)
        await self.validade_len_sku(catalogo.sku)
        await self.validate_len_product_name(catalogo.name)
        await self.validate_product_exist(catalogo.seller_id, catalogo.sku)

    async def save(self, catalogo: Catalogo) -> Catalogo:
        return await super().create(catalogo)
    
    async def delete(self, seller_id: str, sku: str) -> None:
        """
        Deleta um produto do catálogo.
        """
        seller_id = seller_id.lower()
        product = await self.find_product(seller_id, sku, raise_exception=True)
        if product is None:
            raise ProductNotExistException()

        await self.repository.delete(product)

    async def find_product(self, seller_id: str, sku: str, raise_exception: bool = True) -> Catalogo | None:
        product = await super().find_product(seller_id, sku)
        if not product and raise_exception:
            raise ProductNotExistException()
        return product
    
    async def find_by_seller_id(self, seller_id):
        """
        Busca todos os produtos no catálogo com base no seller_id.
        """
        seller_id = seller_id.lower()
        result = await super().find_by_seller_id(seller_id)
        if not result:
            raise SellerIDNotExistException()
        return result
    
    async def find_by_filter(self, seller_id: str, paginator: Paginator = None, name_like: str = None) -> list[Catalogo]:
        seller_id = seller_id.lower()
        # Busca todos os produtos do seller
        result = await super().find_by_seller_id(seller_id)
        if not result:  
            raise SellerIDNotExistException()
        # Filtro por name_like
        filter_name = [item for item in result if name_like.lower() in item.name.lower()]
        if not filter_name:
            raise LikeNotFoundException()
        # Paginação
        if paginator:
            return paginator.paginate(results=result)
        return result

    async def validate_product_exist(self, seller_id: str, sku: str) -> None:
        """
        Valida se um produto pode ser criado verificando se já existe um produto com o mesmo seller_id e SKU.
        """
        product_exist = await self.find_product(seller_id, sku, raise_exception=False)
        if product_exist:
            raise ProductAlreadyExistsException()
        
    async def validate_len_product_name(self, name: str) -> None:
        """
        Valida o tamanho do nome do produto.
        """
        if not name or name.strip() == "" or not (2 <= len(name.strip()) <= 200):
            raise ProductNameLengthException()

    async def validade_len_sku(self, sku: str) -> None:
        """
        Valida o SKU.
        """
        if not isinstance(sku, str) or not sku.strip() or len(sku.strip()) < 2:
            raise SKULengthException()
        
    async def validade_len_seller_id(self, seller_id: str) -> None:
        """
        Valida o seller_id.
        """
        if not isinstance(seller_id, str) or not seller_id.strip() or len(seller_id.strip()) < 2:
            raise SellerIDException()
        
    async def update_product_partial(self, seller_id: str, sku: str, update_payload: CatalogoUpdate) -> Catalogo:
        """
        Atualiza parcialmente um produto no catálogo com base no seller_id e sku.
        """
        seller_id = seller_id.lower()

        # Busca o produto atual
        product_to_update = await self.find_product(seller_id, sku, raise_exception=True)

        if not product_to_update:
            raise ProductNotExistException()

        #exclude_unset=True: somente os campos que foram enviados no payload serão atualizados
        update_data_for_service = update_payload.model_dump(exclude_unset=True)

        if not update_data_for_service:
            raise NoFieldsToUpdateException()

        # Verifica se os dados enviados são iguais aos já existentes
        if all(getattr(product_to_update, key, None) == value for key, value in update_data_for_service.items()):
            raise NoFieldsToUpdateException()

        if "name" in update_data_for_service and update_data_for_service["name"] is not None:
            await self.validate_len_product_name(update_data_for_service["name"])

        updated_product = await super().update(seller_id, update_payload)
        return updated_product

