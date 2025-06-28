import pytest
from app.models.base import UserModel
from app.api.common.auth_handler import do_auth, get_current_user, UserAuthInfo

@pytest.fixture(autouse=True)
def mock_do_auth(monkeypatch):
    async def fake_do_auth(request=None, *args, **kwargs):
        print("MOCK DO_AUTH CHAMADO")
        fake_user = UserModel(name="fake-user", server="fake-server")
        fake_user_info = UserAuthInfo(user=fake_user, trace_id=None, sellers=["magalu11", "magalu10", "sellerapi1", "magalu1", "magalu2"])
        if request is not None and hasattr(request, "state"):
            request.state.user = fake_user_info
        return fake_user_info

    # Patch global
    monkeypatch.setattr("app.api.common.auth_handler.do_auth", fake_do_auth)
    monkeypatch.setattr("app.api.common.auth_handler.get_current_user", fake_do_auth)

    # Patch local no router v2
    import app.api.v2.routers.catalogo_seller_router as router_v2
    monkeypatch.setattr(router_v2, "do_auth", fake_do_auth)
    monkeypatch.setattr(router_v2, "get_current_user", fake_do_auth)

    # Mocka do_auth (usado como Depends em routers)
    monkeypatch.setattr("app.api.common.auth_handler.do_auth", fake_do_auth)
    # Mocka get_current_user (usado como Depends em endpoints)
    monkeypatch.setattr("app.api.common.auth_handler.get_current_user", fake_do_auth)