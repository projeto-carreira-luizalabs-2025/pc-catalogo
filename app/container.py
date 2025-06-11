from dependency_injector import containers, providers

from app.integrations.database.mongo_client import MongoClient

from app.repositories import CatalogoRepository

from app.services import CatalogoService, HealthCheckService
from app.settings.app import AppSettings



class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(AppSettings)

    # -----------------------
    # ** Integrações com o BD
    # Em uma aplicação normal teríamos apenas
    # um cliente de banco de dados

    mongo_client = providers.Singleton(MongoClient, config.app_db_url_mongo)

    # -----------------------
    # ** Repositórios
    #

    catalogo_repository = providers.Singleton(CatalogoRepository, mongo_client)

    # -----------------------
    # ** Servicos
    #
    catalogo_service = providers.Singleton(CatalogoService, catalogo_repository)

    health_check_service = providers.Singleton(
        HealthCheckService, checkers=config.health_check_checkers, settings=settings
    )

