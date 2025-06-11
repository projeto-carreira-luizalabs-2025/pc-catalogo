from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Header, status

from app.api.common.schemas import ListResponse, Paginator, get_request_pagination

from ..schemas.catalogo_schema import CatalogoCreate, CatalogoResponse, CatalogoUpdate
from . import CATALOGO_PREFIX

from app.models import CatalogoModel

if TYPE_CHECKING:
    from app.services import CatalogoService

router = APIRouter(prefix=CATALOGO_PREFIX, tags=["CRUD Catálogo v2"])

#BUSCA PRODUTO POR SELLER_ID PAGINADO
@router.get(
    "",
    response_model=ListResponse[CatalogoResponse],
    status_code=status.HTTP_200_OK,
    summary="Buscar produtos por filtro",
    description=
    """
    Retorna os produtos do seller, podendo ser filtrado pelo nome (like).

        Parâmetros:
            
            - name_like: Filtro pelo nome.
            - _limit: Limite de resultados por página.
            - _offset: Deslocamento para paginação.
            - _sort: Ordenação dos resultados.
            - seller_id: Identificador do vendedor.

        Retorna:

            Os produtos cadastrados de acordo com a busca.

    """,

)
@inject
async def get_by_seller_id_paginado(
    seller_id: str = Header(..., description="Identificador do vendedor"),
    name_like: str = None,  
    paginator: Paginator = Depends(get_request_pagination),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    results = await catalogo_service.find_by_filter(
        seller_id=seller_id,
        paginator=paginator,
        name_like=name_like
    )
    return ListResponse(results=results, meta=None)

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
    catalogo: CatalogoCreate,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    """
    Cria um novo produto no catálogo. Não pode haver um `seller_id` + `sku` já cadastrado.
    """
    catalogo_model = CatalogoModel(**catalogo.model_dump(), seller_id=seller_id)
    catalogo_model = await catalogo_service.create(catalogo_model)
    return CatalogoResponse(**catalogo_model.model_dump())

#ATUALIZA UM PRODUTO
@router.put(
    "/{sku}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Atualiza todos os dados de um produto",
    response_model=CatalogoResponse,
    description=
    """
    Atualiza todos os dados de um produto"

        Parâmetros:

            - sku: Identificador do produto.
            - seller_id: Identificador do vendedor.
            - name: Nome do produto.

        Retorna:

            O produto com os dados atualizados.

    """,
)
@inject
async def put_something(
    sku: str,
    catalogo: CatalogoUpdate,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    """
    Atualiza os dados de um produto.
    """

    catalogo_model = CatalogoModel(**catalogo.model_dump(), seller_id=seller_id, sku=sku)

    catalogo_model = await catalogo_service.update_by_sellerid_sku(seller_id, sku, catalogo_model)
    catalogo_response = catalogo_model.model_dump()

    return catalogo_response

#ATUALIZA PARCIALMENTE UM PRODUTO
@router.patch(
    "/{sku}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Atualiza os dados de um produto parcialmente",
    response_model=CatalogoResponse,
    description=
    """
    Atualiza os dados de um produto parcialmente"

        Parâmetros:

            - sku: Identificador do produto.
            - seller_id: Identificador do vendedor.
            - name: Nome do produto.

        Retorna:

            O produto com os dados atualizados.

    """,
)
@inject
async def patch_something(
    sku: str,
    catalogo: CatalogoUpdate,
    seller_id: str = Header(..., description="Identificador do vendedor"),
    catalogo_service: "CatalogoService" = Depends(Provide["catalogo_service"]),
):
    """
    Atualiza o nome de um produto.
    """

    # Aqui para mim se enviou None então não vou atualizar
    patch_something_dict = catalogo.model_dump(exclude_none=True, exclude_unset=True)
    catalogo_model = await catalogo_service.patch_by_sellerid_sku(seller_id, sku, patch_something_dict)
    catalogo_response = catalogo_model.model_dump()

    return catalogo_response

#DELETA UM PRODUTO
@router.delete(
        "/{sku}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Deletar o produto",
        description=
        """
            Deleta um produto do catálogo com base no seller_id e SKU.

            Parâmetros:
                sku: Código do produto.
                seller_id: ID do vendedor.

            Retorna:
                204 - No content.

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
    return await catalogo_service.delete_by_sellerid_sku(seller_id, sku)

