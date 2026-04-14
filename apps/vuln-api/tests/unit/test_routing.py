"""Unit tests for the Starlette decorator router shim."""

from flask import Flask, request as flask_request
import pytest
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from app.asgi import http_exception_handler
from app.routing import DecoratorRouter, get_json_or_default


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


def test_decorator_router_forwards_path_params_to_handler():
    router = DecoratorRouter(routes=[])

    @router.route("/api/v1/things/<thing_id>")
    async def handler(request, thing_id):
        return JSONResponse({"thing_id": thing_id})

    app = Starlette(routes=router.routes)

    with TestClient(app) as client:
        response = client.get("/api/v1/things/abc123")

    assert response.status_code == 200
    assert response.json() == {"thing_id": "abc123"}


def test_decorator_router_prioritizes_static_routes_over_dynamic_matches():
    router = DecoratorRouter(routes=[])

    @router.route("/api/v1/licenses/<license_id>")
    async def dynamic_handler(request, license_id):
        return JSONResponse({"license_id": license_id})

    @router.route("/api/v1/licenses/export")
    async def static_handler(request):
        return JSONResponse({"export": True})

    app = Starlette(routes=router.routes)

    with TestClient(app) as client:
        response = client.get("/api/v1/licenses/export")

    assert response.status_code == 200
    assert response.json() == {"export": True}


def test_decorator_router_demotes_path_converters_below_normal_params():
    router = DecoratorRouter(routes=[])

    @router.route("/api/v1/files/<path:file_path>")
    async def path_handler(request, file_path):
        return JSONResponse({"kind": "path", "file_path": file_path})

    @router.route("/api/v1/files/<file_id>")
    async def param_handler(request, file_id):
        return JSONResponse({"kind": "param", "file_id": file_id})

    app = Starlette(routes=router.routes)

    with TestClient(app) as client:
        response = client.get("/api/v1/files/report.csv")

    assert response.status_code == 200
    assert response.json() == {"kind": "param", "file_id": "report.csv"}


@pytest.mark.parametrize(
    ("request_kwargs", "expected_status", "expected_json"),
    [
        ({"data": b""}, 415, None),
        ({"data": "{", "content_type": "application/json"}, 400, None),
        ({"data": "null", "content_type": "application/json"}, 200, {"data": {}}),
        ({"data": '{"a":1}', "content_type": "application/json"}, 200, {"data": {"a": 1}}),
    ],
)
def test_get_json_or_default_matches_current_flask_request_get_json_semantics(
    request_kwargs,
    expected_status,
    expected_json,
):
    flask_app = Flask(__name__)
    flask_app.config["TESTING"] = True

    @flask_app.post("/probe")
    def flask_probe():
        data = flask_request.get_json() or {}
        return {"data": data}

    router = DecoratorRouter(routes=[])

    @router.route("/probe", methods=["POST"])
    async def starlette_probe(request):
        data = await get_json_or_default(request)
        return JSONResponse({"data": data})

    asgi_app = Starlette(
        routes=router.routes,
        exception_handlers={HTTPException: http_exception_handler, Exception: http_exception_handler},
    )

    asgi_kwargs = {"content": request_kwargs["data"]}
    if "content_type" in request_kwargs:
        asgi_kwargs["headers"] = {"content-type": request_kwargs["content_type"]}

    with flask_app.test_client() as flask_client, TestClient(asgi_app) as asgi_client:
        flask_response = flask_client.post("/probe", **request_kwargs)
        asgi_response = asgi_client.post("/probe", **asgi_kwargs)

    assert flask_response.status_code == expected_status
    assert asgi_response.status_code == expected_status
    if expected_json is not None:
        assert flask_response.get_json() == expected_json
        assert asgi_response.json() == expected_json
