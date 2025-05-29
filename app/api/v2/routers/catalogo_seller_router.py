from typing import TYPE_CHECKING, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, status

from app.api.common.schemas import ListResponse, Paginator, UuidType, get_request_pagination

from ..schemas.catalogo_schema import CatalogoCreate, CatalogoResponse, CatalogoUpdate
from . import CATALOGO_PREFIX

if TYPE_CHECKING:
    from app.services import CatalogoService

router = APIRouter(prefix=CATALOGO_PREFIX, tags=["CRUD Catálogo v2"])



#BUSCA PRODUTO POR SELLER_ID PAGINADO
@router.get(
    "",
    response_model=ListResponse[CatalogoResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar produtos por filtro",
    description="Retorna os produtos do seller filtrando por nome (like)."
)
@inject
async def get_by_seller_id_paginado(
    seller_id: str = Header(..., description="Identificador do vendedor"),
    name_like: str = None,  
    paginator: Paginator = Depends(get_request_pagination),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    return await catalogo_service.find_by_filter(
        seller_id, paginator=paginator, name_like=name_like
    )

#BUSCAR PRODUTO POR SELLER_ID + SKU 
@router.get(
    "/{sku}",
    response_model=CatalogoResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar produto por Seller_id e SKU",
    description=
    """
        Retorna um produto específico do catálogo com base no seller_id e SKU.

    """,
)
@inject
async def get_product(
    sku: str,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    return await catalogo_service.find_product(seller_id, sku)

#CADASTRO DE UM PRODUTO
@router.post(
    "",
    response_model=CatalogoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um novo produto",
    description=
    """
    Cria um novo produto no catálogo com base nos dados fornecidos.

        Parâmetros:
            
            - seller_id: Identificador do vendedor.
            - sku: Identificador do produto.
            - name: Nome do produto.

        Retorna:

            O produto adicionado.

    """,
)
@inject
async def create(
    catalogo: CatalogoCreate, catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"])
):
    return await catalogo_service.create(catalogo)

#ATUALIZA O NOME DE UM PRODUTO
@router.patch(
    "/{sku}",
    response_model=CatalogoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar produto",
)
@inject
async def update_by_id(
    sku: str,
    catalogo: CatalogoUpdate,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    return await catalogo_service.update_product_partial(seller_id, sku, catalogo)

#DELETA UM PRODUTO
@router.delete(
        "/{sku}",
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
    sku: str,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    return await catalogo_service.delete(seller_id, sku)

##BUSCAR TODOS OS PRODUTOS
@router.get("/all",
    response_model=ListResponse[CatalogoResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar todos os produtos",
    description=
    """
    Retorna todos os produtos cadastrados no catálogo.

        Atributos:

            - seller_id: Identificador do vendedor.
            - sku: Identificador do produto.
            - name: Nome do produto.

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
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    results = await catalogo_service.find(paginator=paginator, filters={})

    return paginator.paginate(results=results)

#BUSCA TODOS OS PRODUTOS CADASTRADOS POR UM SELLER_ID
@router.get(
    "/all-by-seller-id",
    response_model=List[CatalogoResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar todos os produtos de um seller",
    description=
    """
        Retorna todos os produtos cadastrados no catálogo com base no seller_id.

        Parâmetros:
            seller_id: ID do seller.

        Retorna:
            Uma lista de produtos associados ao seller_id fornecido.

        Erros:
            404 - SellerID não encontrado.
    """,
)
@inject
async def get_by_seller_id(
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    return await catalogo_service.find_by_seller_id(seller_id)





