from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel, Field
from .app import AppSettings


class FilterConfig(BaseModel):
    max_length: int = Field(default=100, description="Tamanho máximo para filtro")
    min_length: int = Field(default=1, description="Tamanho mínimo para filtro")


class PaginationConfig(BaseModel):
    default_limit: int = Field(
        default=10,
        description="Determina a quantidade padrão de registros a serem retornados",
    )
    max_limit: int = Field(
        default=100,
        description="Determina a quantidade máxima de registros a serem retornados",
    )


class ApiSettings(AppSettings):
    server_port: int = Field(default=8000, title="Porta da aplicação")

    openapi_path: str = Field(
        default="/openapi.json",
        title="Caminho para exportar o OpenAPI, deixar vazio para não exportar.",
    )

    health_check_base_path: str = Field(
        default="/api",
        title="Caminho para o health check. A partir dele haverão dois recursos: ping e health",
    )

    cors_origins: list[str] = Field(default=["*"], title="Origens permitidas para CORS")

    access_log_ignored_urls: set[str] | None = Field(
        default=None,
        title="URLs da API que não devem ter o log de acesso emitido",
    )

    access_log_headers_to_log: set[str] | None = Field(
        default=None,
        title="Headers que podem aparecer no log de requisições",
    )

    access_log_headers_to_obfuscate: set[str] | None = Field(
        default=None,
        title="Headers que devem ser ofuscados no log de requisições",
    )

    pagination: PaginationConfig = Field(default=PaginationConfig(), description="Configurações de paginação")

    filter_config: FilterConfig = Field(default=FilterConfig(), description="Configurações de filtros")

    enable_seller_resources: bool = Field(default=True, description="Habilita Recursos de APIs do contexto de Seller")

    enable_channel_resources: bool = Field(default=True, description="Habilita Recursos de APIs do contexto de Canal")

    @property
    def server_reload(self) -> bool:  # pragma: no cover
        return self.env.is_development()


api_settings = ApiSettings()
