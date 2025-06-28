import dotenv
dotenv.load_dotenv()
import os
from fastapi import FastAPI

from app.container import Container
from app.settings import api_settings

ENV = os.getenv("ENV", "production")
is_dev = ENV == "dev"

dotenv.load_dotenv(override=is_dev)
print("DEBUG - APP_OPENID_WELLKNOWN:", os.getenv("APP_OPENID_WELLKNOWN"))
print("DEBUG - APP_OPENID_WELLKNOWN:", os.getenv("APP_DB_URL_MONGO"))

def init() -> FastAPI:
    print("API Settings:", api_settings.model_dump())
    print("APP_OPENID_WELLKNOWN:", os.getenv("APP_OPENID_WELLKNOWN"))
    from app.api.api_application import create_app
    from app.api.router import routes as api_routes

    container = Container()

    container.config.from_pydantic(api_settings)
    print("DEBUG - config.app_openid_wellknown:", container.config.app_openid_wellknown())
    app_api = create_app(api_settings, api_routes)
    app_api.container = container  # type: ignore[attr-defined]

    # Autowiring
    container.wire(modules=["app.api.common.routers.health_check_routers"])
    container.wire(modules=["app.api.v1.routers.catalogo_seller_router"])
    container.wire(modules=["app.api.v2.routers.catalogo_seller_router"])
    

    # Outros middlewares podem ser adicionados aqui se necessário

    return app_api


app = init()
