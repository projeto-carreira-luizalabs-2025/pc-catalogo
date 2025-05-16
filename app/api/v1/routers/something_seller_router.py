from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination
from app.container import Container

from ..schemas.something_schema import SomethingCreate, SomethingResponse, SomethingUpdate
from . import SOMETHING_PREFIX

if TYPE_CHECKING:
    from app.services import SomethingService

router = APIRouter(prefix=SOMETHING_PREFIX, tags=["CRUD Catálogo"])

##BUSCAR TODOS OS PRODUTOS
@router.get("",
    response_model=ListResponse[SomethingResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar todos os produtos",
    description=
    """
    Retorna todos os produtos cadastrados no catálogo.

        Atributos:

            - seller_id: Identificador do vendedor.
            - sku: Identificador do produto.
            - product_name: Nome do produto.

        Exemplo:

        {
            "seller_id": "magalu",
            "sku": "mon-27-144hz",
            "quantidade": "Monitor de 27 polegadas 144Hz Full HD", 
        }

    """,
)
@inject
async def get_all_products(
    
    paginator: Paginator = Depends(get_request_pagination),
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):

    results = await something_service.find(paginator=paginator, filters={})

    return paginator.paginate(results=results)

#BUSCAR PRODUTO POR SELLER_ID + SKU
@router.get(
    "/{seller_id}/{sku}",
    response_model=SomethingResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar produto por Seller_id e SKU",
    description=
    """
        Retorna um produto específico do catálogo com base no seller_id e SKU.

    """,
)
@inject
async def get_product(
    seller_id: str,
    sku: str,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    return await something_service.find_product(seller_id, sku)


#CADASTRO DE UM PRODUTO
@router.post(
    "",
    response_model=SomethingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo produto",
    description=
    """
    Cria um novo produto no catálogo com base nos dados fornecidos.

        Parâmetros:
            
            - seller_id: Identificador do vendedor.
            - sku: Identificador do produto.
            - product_name: Nome do produto.

        Retorna:

            O produto adicionado.

    """,
)
@inject
async def create(
    something: SomethingCreate, something_service: "SomethingService" = Depends(Provide[Container.something_service])
):
    return await something_service.create(something)

#ATUALIZA O NOME DE UM PRODUTO
@router.patch(
    "/{seller_id}/{sku}",
    response_model=SomethingResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def update_by_id(
    seller_id: str,
    sku: str,
    something: SomethingUpdate,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    return await something_service.update(seller_id, something)


#DELETA UM PRODUTO
@router.delete(
        "/{seller_id}/{sku}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Deletar produto",
        description=
        """
            Deleta um produto do catálogo com base no seller_id e SKU.

            Parâmetros:
                seller_id: ID do vendedor.
                sku: Código do produto.

            Erros:
                404 - Este produto não existe.
        """
        
        )
@inject
async def delete(
    seller_id: str,
    sku: str,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    await something_service.delete_product(seller_id, sku)



"""nao utilizadas"""

#Busca o produto pelo ID
@router.get(
    "/{seller_id}",
    response_model=SomethingResponse,
    status_code=status.HTTP_200_OK,
)
@inject
async def get_by_id(
    seller_id: str,
    something_service: "SomethingService" = Depends(Provide[Container.something_service]),
):
    return await something_service.find_by_id(seller_id)