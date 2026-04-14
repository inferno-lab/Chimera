"""
Decorator-friendly Router that wraps Starlette's Router.

Starlette uses declarative Route() lists, but our codemod produces
Flask-style @router.route('/path') decorators. This shim bridges the gap
so 486 route registrations don't need manual conversion to declarative style.
"""

import asyncio
import inspect
import json
import re
from functools import wraps
from types import SimpleNamespace

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Router as _StarletteRouter

_PATH_PARAM_RE = re.compile(r"<(?:(?P<converter>[a-zA-Z_][a-zA-Z0-9_]*):)?(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)>")
_STARLETTE_PATH_PARAM_RE = re.compile(r"{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)(?::(?P<converter>[a-zA-Z_][a-zA-Z0-9_]*))?}")
_CONVERTER_MAP = {
    "int": "int",
    "float": "float",
    "path": "path",
    "uuid": "uuid",
}


def _is_json_media_type(content_type: str | None) -> bool:
    if not content_type:
        return False

    media_type = content_type.split(";", 1)[0].strip().lower()
    return media_type == "application/json" or (
        media_type.startswith("application/") and media_type.endswith("+json")
    )


def build_http_exception_body(
    *,
    status_code: int,
    detail: str,
    path: str,
    method: str,
    headers: dict | None = None,
    query_params: dict | None = None,
) -> dict:
    """Build the shared JSON error payload used by ASGI and Flask-compat routes."""
    from app.config import app_config

    body = {
        "error": detail,
        "status": status_code,
        "path": path,
        "method": method,
    }

    if getattr(app_config, "debug", False):
        body["debug"] = {
            "headers": headers or {},
            "query_params": query_params or {},
        }

    return body


class DecoratorRouter(_StarletteRouter):
    """Router subclass that supports @router.route() decorators."""

    @staticmethod
    def _route_sort_key(route: Route) -> tuple:
        path = getattr(route, "path", "")
        segments = [segment for segment in path.split("/") if segment]

        def _segment_key(segment: str) -> tuple:
            match = _STARLETTE_PATH_PARAM_RE.fullmatch(segment)
            if not match:
                return (0, -len(segment), segment)

            converter = match.group("converter")
            if converter == "path":
                return (3, 0, segment)
            if converter:
                return (1, 0, segment)
            return (2, 0, segment)

        return (tuple(_segment_key(segment) for segment in segments), -len(segments), path)

    @staticmethod
    def _normalize_path(path: str) -> str:
        def _replace(match: re.Match[str]) -> str:
            converter = match.group("converter")
            name = match.group("name")
            starlette_converter = _CONVERTER_MAP.get(converter or "")
            if starlette_converter:
                return f"{{{name}:{starlette_converter}}}"
            return f"{{{name}}}"

        return _PATH_PARAM_RE.sub(_replace, path)

    @staticmethod
    def _denormalize_path(path: str) -> str:
        def _replace(match: re.Match[str]) -> str:
            converter = match.group("converter")
            name = match.group("name")
            if converter:
                return f"<{converter}:{name}>"
            return f"<{name}>"

        return _STARLETTE_PATH_PARAM_RE.sub(_replace, path)

    def route(self, path: str, methods: list[str] | None = None, **kwargs):
        """Register a route handler via decorator, Flask-style."""
        if methods is None:
            methods = ["GET"]

        normalized_path = self._normalize_path(path)

        def decorator(func):
            signature = inspect.signature(func)
            accepts_var_kwargs = any(
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in signature.parameters.values()
            )

            @wraps(func)
            async def endpoint(request):
                path_kwargs = request.path_params
                if not accepts_var_kwargs:
                    path_kwargs = {
                        name: value for name, value in request.path_params.items() if name in signature.parameters
                    }

                result = func(request, **path_kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return result

            self.routes.append(Route(normalized_path, endpoint, methods=methods, **kwargs))
            # Preserve Flask/Werkzeug-like specificity so static paths
            # and typed params win over broad catch-all converters.
            self.routes.sort(key=self._route_sort_key)
            return func
        return decorator

    def get(self, path: str, **kwargs):
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path: str, **kwargs):
        return self.route(path, methods=['POST'], **kwargs)

    def put(self, path: str, **kwargs):
        return self.route(path, methods=['PUT'], **kwargs)

    def delete(self, path: str, **kwargs):
        return self.route(path, methods=['DELETE'], **kwargs)

    def patch(self, path: str, **kwargs):
        return self.route(path, methods=['PATCH'], **kwargs)


async def get_json_or_default(request: Request, default=None, *, strict: bool = False):
    """Mirror Flask JSON parsing semantics for migrated Starlette handlers."""
    content_type = str(request.headers.get("content-type", ""))
    if not _is_json_media_type(content_type):
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")

    try:
        data = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Malformed JSON body") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Malformed JSON body") from exc

    if data is None:
        if strict:
            raise HTTPException(status_code=400, detail="JSON body is required")
        return {} if default is None else default
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="JSON body must be an object")
    return data


class FlaskRequestAdapter:
    """Expose the Starlette request surface migrated handlers rely on."""

    def __init__(self, flask_request, path_params: dict[str, str]):
        self._request = flask_request
        self.path_params = path_params
        self.query_params = flask_request.args
        self.headers = flask_request.headers
        self.method = flask_request.method
        self.url = SimpleNamespace(path=flask_request.path)

    async def json(self):
        return self._request.get_json()


def _coerce_flask_response(result):
    from flask import Response as FlaskResponse

    if isinstance(result, FlaskResponse):
        return result

    if hasattr(result, "status_code") and hasattr(result, "headers"):
        body = getattr(result, "body", b"")
        response = FlaskResponse(body, status=getattr(result, "status_code", 200))
        for header, value in result.headers.items():
            if header.lower() == "content-length":
                continue
            response.headers[header] = value
        media_type = getattr(result, "media_type", None)
        if media_type and "Content-Type" not in response.headers:
            response.mimetype = media_type
        return response

    return result


def register_flask_compat_routes(app, router: DecoratorRouter, *, endpoint_prefix: str) -> None:
    """Mirror migrated Starlette routes into Flask while the transition is in flight."""
    from flask import request as flask_request

    for index, route in enumerate(router.routes):
        methods = sorted(method for method in (route.methods or {"GET"}) if method not in {"HEAD", "OPTIONS"})
        flask_path = DecoratorRouter._denormalize_path(getattr(route, "path", ""))
        safe_path = re.sub(r"[^a-zA-Z0-9_]+", "_", flask_path).strip("_") or "root"
        endpoint_name = f"{endpoint_prefix}_{index}_{safe_path}"

        def compat_view(_route=route, **kwargs):
            adapter = FlaskRequestAdapter(flask_request, kwargs)
            try:
                result = _route.endpoint(adapter)
                if inspect.isawaitable(result):
                    result = asyncio.run(result)
            except HTTPException as exc:
                result = JSONResponse(
                    build_http_exception_body(
                        status_code=exc.status_code,
                        detail=str(exc.detail),
                        path=flask_request.path,
                        method=flask_request.method,
                        headers=dict(flask_request.headers),
                        query_params=dict(flask_request.args),
                    ),
                    status_code=exc.status_code,
                )
            return _coerce_flask_response(result)

        app.add_url_rule(flask_path, endpoint=endpoint_name, view_func=compat_view, methods=methods)
