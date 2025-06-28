from fastapi import HTTPException, status
from fastapi.requests import Request


"""async def get_seller_id(request: Request) -> str:
    seller_id = request.headers.get("x-seller-id")
    if not seller_id:
        raise HTTPException(
            # XXX Teria um outro melhor?
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Faltando cabeçalho x-seller-id",
        )

    return seller_id"""

async def get_seller_id(request: Request) -> str:
    print("HEADERS RECEBIDOS:", dict(request.headers), flush=True)

    seller_id = (
        request.headers.get("x-seller-id")
        or request.headers.get("seller-id")
    )
    if not seller_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Faltando cabeçalho seller-id ou x-seller-id",
        )
    return seller_id