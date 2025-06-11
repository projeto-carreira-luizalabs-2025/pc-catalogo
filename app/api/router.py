from fastapi import APIRouter

from app.api.v1 import router_seller as v1_router_seller
from app.api.v2 import router_seller as v2_router_seller

routes = APIRouter()

#routes.include_router(v1_router_seller)
routes.include_router(v2_router_seller)
