import httpx
import jwt

# ----- Exceções -----

# Criando exceções genéricas aqui mesmo


class OAuthException(Exception):
    """
    Exceção geral de autenticação
    """


class TokenExpiredException(OAuthException):
    """
    Token expirou
    """


class InvalidTokenException(OAuthException):
    """
    Token inválido
    """


class KeycloakAdapter:
    def __init__(self, well_known_url: str):
        print("DEBUG - wellknown_url recebido:", well_known_url, flush=True)
        
        self.well_known_url = str(well_known_url)
        self._well_knwon: dict | None = None
        self._public_keys: list[dict] | None = None

    def get_well_knwon(self) -> dict:
        if self._well_knwon is None:
            self._well_knwon = self._load_well_known()
        return self._well_knwon

    def _load_well_known(self):
        with httpx.Client() as http_client:
            response = http_client.get(self.well_known_url)
            response.raise_for_status()
            wk = response.json()
        return wk

    def get_authorization_endpoint(self):
        well_kwnon = self.get_well_knwon()
        authorization_endpoint = well_kwnon["authorization_endpoint"]
        return authorization_endpoint

    async def get_public_keys(self):
        if self._public_keys is None:
            self._public_keys = await self._fetch_public_keys()
        return self._public_keys

    async def _fetch_public_keys(self) -> list:
        well_known = self.get_well_knwon()
        jwks_uri = well_known["jwks_uri"]
        async with httpx.AsyncClient() as http_client:
            jwks_response = await http_client.get(jwks_uri)
            jwks_response.raise_for_status()

            keys = jwks_response.json()["keys"]

            return keys

    @staticmethod
    def get_token_header(token: str) -> dict:
        header = jwt.get_unverified_header(token)
        return header

    @classmethod
    def get_header_info_from_token(cls, token: str) -> tuple[str, str]:
        header = cls.get_token_header(token)
        kid = header.get("kid")
        alg = header.get("alg")

        return kid, alg

    async def get_alg_key_for_kid(self, kid) -> dict:
        # Procurando pela chave específica
        public_keys = await self.get_public_keys()
        key = next((public_key for public_key in public_keys if public_key.get("kid") == kid), None)
        if not key:
            raise InvalidTokenException(f"Chave '{kid}' não encontrada")
        return key

    async def validate_token(self, token: str) -> dict:
        print("DEBUG - Token recebido:", token[:40], flush=True)
        try:
            # Obendo o kid (key id) no cabeçalho
            kid, alg = self.get_header_info_from_token(token)

            key = await self.get_alg_key_for_kid(kid)

            
            # Verificando o token
            jwt_key = jwt.PyJWK(jwk_data=key, algorithm=alg)
            
            info_token = jwt.decode(
                token,
                # Chave pública a ser usada
                jwt_key,
                # Qual é o algoritmo
                algorithms=[alg],
                # Vou validar desconsiderando a audiência
                options={"verify_aud": False},
            )
            print("DEBUG - info_token:", info_token, flush=True)
            return info_token
        except jwt.ExpiredSignatureError as exception:
            raise TokenExpiredException("Token expirou") from exception
        except jwt.InvalidTokenError as exception:
            raise InvalidTokenException("Token inválido") from exception
        except OAuthException:
            raise
        except Exception as e:
            print("DEBUG - Token inválido:", e, flush=True)
    
            raise OAuthException("Falha ao validar o token") from e
