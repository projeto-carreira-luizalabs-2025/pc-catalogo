"""
'Camada' de segurança para a API
"""

from typing import TYPE_CHECKING, Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.common.injector import get_seller_id
from app.common.exceptions import ForbiddenException, UnauthorizedException

from app.integrations.auth.keycloak_adapter import OAuthException

if TYPE_CHECKING:
    from app.integrations.auth.keycloak_adapter import KeycloakAdapter

from app.models.base import BaseModel, UserModel


from app.container import Container
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserAuthInfo(BaseModel):
    user: UserModel
    trace_id: str | None
    sellers: list[str]

    @staticmethod
    def to_sellers(sellers: str | None) -> list[str]:
        sellers = sellers.split(",") if sellers else []
        return sellers



@inject
async def do_auth(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)],
    seller_id: str = Depends(get_seller_id),
    openid_adapter: "KeycloakAdapter" = Depends(Provide[Container.keycloak_adapter]),
)-> UserAuthInfo:
    """
    Responsável por fazer a autenticação com algum IDP OpenId.
    """

    try:
        info_token = await openid_adapter.validate_token(token)
    except OAuthException as exception:
        # XXX Poderíamos especializar as exceções
        raise UnauthorizedException from exception

    user_info = UserAuthInfo(
        user=UserModel(
            name=info_token.get("sub"),
            server=info_token.get("iss"),
        ),
        trace_id=request.state.trace_id,
        sellers=UserAuthInfo.to_sellers(info_token.get("sellers")),
    )

# Debug temporário
    print("DEBUG seller_id header:", seller_id)
    print("DEBUG sellers claim:", info_token.get("sellers", None))

    # Nossa autorização (permissão):
    # O usuário pode operar com o seller informado?
    sellers = user_info.sellers

    if seller_id not in sellers:
        raise ForbiddenException([{"message": "não autorizado para trabalhar com este seller"}])

    request.state.user = user_info

    return user_info


async def get_current_user(request: Request) -> UserAuthInfo:
    user = request.state.user
    return user
