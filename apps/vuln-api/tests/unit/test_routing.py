"""Unit tests for the Starlette decorator router shim."""

from app.routing import DecoratorRouter


def test_decorator_router_preserves_simple_flask_style_paths():
    router = DecoratorRouter(routes=[])

    @router.route("/api/v1/things/<thing_id>")
    async def handler(request, thing_id):  # pragma: no cover - route registration only
        return {"thing_id": thing_id}

    assert router.routes[0].path == "/api/v1/things/{thing_id}"


def test_decorator_router_converts_typed_path_parameters():
    router = DecoratorRouter(routes=[])

    @router.route("/api/test/status/<int:code>")
    async def handler(request, code):  # pragma: no cover - route registration only
        return {"code": code}

    assert router.routes[0].path == "/api/test/status/{code:int}"
