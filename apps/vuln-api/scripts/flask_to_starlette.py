#!/usr/bin/env python3
"""
Flask → Starlette codemod using libcst.

Transforms Flask route files into Starlette-compatible async handlers.
Covers ~85% of mechanical changes; manual review required for hotpatch,
file uploads, and render_template_string.

Usage:
    uv run python scripts/flask_to_starlette.py app/blueprints/recorder/routes.py
    uv run python scripts/flask_to_starlette.py app/blueprints/recorder/  # transforms __init__.py + routes.py
    uv run python scripts/flask_to_starlette.py --dry-run app/blueprints/recorder/routes.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import libcst as cst
import libcst.matchers as m


# ---------------------------------------------------------------------------
# Blueprint __init__.py transformer
# ---------------------------------------------------------------------------

class BlueprintInitTransformer(cst.CSTTransformer):
    """Transform Blueprint('name', __name__) → Router() in __init__.py files."""

    def __init__(self):
        self.bp_name: str | None = None
        self.router_name: str | None = None

    def leave_SimpleStatementLine(
        self, original: cst.SimpleStatementLine, updated: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine | cst.RemovalSentinel:
        if len(updated.body) != 1:
            return updated

        stmt = updated.body[0]

        # from flask import Blueprint → from app.routing import DecoratorRouter as Router
        if isinstance(stmt, cst.ImportFrom):
            module_name = stmt.module.value if isinstance(stmt.module, cst.Name) else ""
            if module_name == "flask":
                names = stmt.names
                if isinstance(names, (list, tuple)):
                    has_blueprint = any(
                        isinstance(alias.name, cst.Name) and alias.name.value == "Blueprint"
                        for alias in names
                    )
                    if has_blueprint:
                        return cst.parse_statement(
                            "from app.routing import DecoratorRouter as Router\n"
                        )

        # foo_bp = Blueprint('foo', __name__) → foo_router = Router(routes=[])
        if isinstance(stmt, cst.Assign):
            if (
                len(stmt.targets) == 1
                and m.matches(stmt.value, m.Call(func=m.Name("Blueprint")))
            ):
                old_name = stmt.targets[0].target
                if isinstance(old_name, cst.Name) and old_name.value.endswith("_bp"):
                    self.bp_name = old_name.value
                    self.router_name = old_name.value.replace("_bp", "_router")
                    new_target = cst.AssignTarget(
                        target=cst.Name(self.router_name)
                    )
                    new_value = cst.parse_expression("Router(routes=[])")
                    return updated.with_changes(
                        body=[stmt.with_changes(
                            targets=[new_target],
                            value=new_value,
                        )]
                    )

        return updated


# ---------------------------------------------------------------------------
# Route file transformer
# ---------------------------------------------------------------------------

class FlaskRouteTransformer(cst.CSTTransformer):
    """Transform Flask route handlers to Starlette async handlers."""

    def __init__(self, bp_name: str = "bp"):
        self.bp_name = bp_name
        self.router_name = bp_name.replace("_bp", "_router")
        self._in_route_handler = False
        self._needs_await: set[str] = set()

    # --- Import transforms ---

    def leave_SimpleStatementLine(
        self, original: cst.SimpleStatementLine, updated: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine | cst.RemovalSentinel | cst.FlattenSentinel:
        """Handle Flask import replacement at the statement level."""
        if len(updated.body) != 1:
            return updated

        stmt = updated.body[0]
        if not isinstance(stmt, cst.ImportFrom):
            return updated

        module_str = self._module_to_str(stmt.module)

        # from flask import request, jsonify, ... → Starlette imports
        if module_str == "flask":
            names = stmt.names
            if isinstance(names, (list, tuple)):
                flask_names = {
                    alias.name.value if isinstance(alias.name, cst.Name) else ""
                    for alias in names
                }

                starlette_stmts: list[cst.SimpleStatementLine] = []

                # Request
                if "request" in flask_names:
                    starlette_stmts.append(
                        cst.parse_statement("from starlette.requests import Request\n")
                    )

                # Response types
                response_names = []
                if "jsonify" in flask_names:
                    response_names.append("JSONResponse")
                if "Response" in flask_names:
                    response_names.append("Response")
                if "render_template_string" in flask_names:
                    response_names.append("HTMLResponse")

                if response_names:
                    names_str = ", ".join(response_names)
                    starlette_stmts.append(
                        cst.parse_statement(
                            f"from starlette.responses import {names_str}\n"
                        )
                    )

                # Passthrough names we keep from flask
                kept = flask_names - {
                    "request", "jsonify", "Response", "Blueprint",
                    "render_template_string", "session", "current_app",
                    "make_response", "abort", "send_from_directory", "g",
                }
                if kept:
                    kept_aliases = [cst.ImportAlias(name=cst.Name(n)) for n in sorted(kept)]
                    kept_import = stmt.with_changes(names=kept_aliases)
                    starlette_stmts.append(
                        updated.with_changes(body=[kept_import])
                    )

                if starlette_stmts:
                    return cst.FlattenSentinel(starlette_stmts)
                return cst.RemovalSentinel.REMOVE

        # from . import foo_bp → from . import foo_router
        if self._is_relative_import(stmt):
            names = stmt.names
            if isinstance(names, (list, tuple)):
                new_names = []
                changed = False
                for alias in names:
                    if isinstance(alias.name, cst.Name) and alias.name.value == self.bp_name:
                        new_names.append(
                            alias.with_changes(name=cst.Name(self.router_name))
                        )
                        changed = True
                    else:
                        new_names.append(alias)
                if changed:
                    new_import = stmt.with_changes(names=new_names)
                    return updated.with_changes(body=[new_import])

        return updated

    # --- Route decorator transforms ---

    def leave_Decorator(
        self, original: cst.Decorator, updated: cst.Decorator
    ) -> cst.Decorator:
        # @foo_bp.route(...) → @foo_router.route(...)
        dec = updated.decorator
        if m.matches(dec, m.Call(func=m.Attribute(attr=m.Name("route")))):
            func = dec.func
            if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                if func.value.value == self.bp_name:
                    new_func = func.with_changes(
                        value=cst.Name(self.router_name)
                    )
                    return updated.with_changes(
                        decorator=dec.with_changes(func=new_func)
                    )
        # @foo_bp.get/post/put/delete/patch(...)
        for method in ("get", "post", "put", "delete", "patch"):
            if m.matches(dec, m.Call(func=m.Attribute(attr=m.Name(method)))):
                func = dec.func
                if isinstance(func, cst.Attribute) and isinstance(func.value, cst.Name):
                    if func.value.value == self.bp_name:
                        new_func = func.with_changes(
                            value=cst.Name(self.router_name)
                        )
                        return updated.with_changes(
                            decorator=dec.with_changes(func=new_func)
                        )
        return updated

    # --- Function definition: def → async def, inject request param ---

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        # Check if this function has a route decorator
        for dec in node.decorators:
            dec_str = self._decorator_to_str(dec)
            if self.router_name in dec_str or self.bp_name in dec_str:
                self._in_route_handler = True
                return True
        self._in_route_handler = False
        return True

    def leave_FunctionDef(
        self, original: cst.FunctionDef, updated: cst.FunctionDef
    ) -> cst.FunctionDef:
        if not self._in_route_handler:
            return updated

        self._in_route_handler = False

        # Make async
        if not updated.asynchronous:
            updated = updated.with_changes(
                asynchronous=cst.Asynchronous()
            )

        # Inject `request: Request` as first parameter
        params = updated.params
        param_names = [
            p.name.value for p in params.params
            if isinstance(p.name, cst.Name)
        ]
        if "request" not in param_names:
            request_param = cst.Param(
                name=cst.Name("request"),
                annotation=cst.Annotation(annotation=cst.Name("Request")),
            )
            new_params = [request_param] + list(params.params)
            updated = updated.with_changes(
                params=params.with_changes(params=new_params)
            )

        return updated

    # --- Expression transforms inside route handlers ---

    def leave_Call(self, original: cst.Call, updated: cst.Call) -> cst.BaseExpression:
        # jsonify({...}) → JSONResponse({...})
        if m.matches(updated, m.Call(func=m.Name("jsonify"))):
            return updated.with_changes(func=cst.Name("JSONResponse"))

        # request.get_json() → await request.json()
        if m.matches(
            updated,
            m.Call(func=m.Attribute(value=m.Name("request"), attr=m.Name("get_json"))),
        ):
            new_call = updated.with_changes(
                func=cst.Attribute(value=cst.Name("request"), attr=cst.Name("json")),
                args=[],
            )
            return cst.Await(expression=new_call)

        return updated

    # --- Attribute transforms ---

    def leave_Attribute(
        self, original: cst.Attribute, updated: cst.Attribute
    ) -> cst.BaseExpression:
        # request.args → request.query_params
        if m.matches(updated, m.Attribute(value=m.Name("request"), attr=m.Name("args"))):
            return updated.with_changes(attr=cst.Name("query_params"))

        # request.remote_addr → request.client.host
        if m.matches(
            updated, m.Attribute(value=m.Name("request"), attr=m.Name("remote_addr"))
        ):
            return cst.Attribute(
                value=cst.Attribute(value=cst.Name("request"), attr=cst.Name("client")),
                attr=cst.Name("host"),
            )

        # request.path → request.url.path
        if m.matches(updated, m.Attribute(value=m.Name("request"), attr=m.Name("path"))):
            return cst.Attribute(
                value=cst.Attribute(value=cst.Name("request"), attr=cst.Name("url")),
                attr=cst.Name("path"),
            )

        # request.json (property access, not call) → request.json (stays — caller must await)
        # This is fine — the Call handler above catches request.get_json()

        return updated

    # --- Return tuple transforms: return JSONResponse({...}), 400 ---

    def leave_Return(
        self, original: cst.Return, updated: cst.Return
    ) -> cst.Return:
        if updated.value is None:
            return updated

        # return JSONResponse({...}), code → return JSONResponse({...}, status_code=code)
        if m.matches(updated.value, m.Tuple()):
            elements = updated.value.elements
            if len(elements) == 2:
                first = elements[0].value
                second = elements[1].value

                # Check if first element is a JSONResponse call
                if m.matches(first, m.Call(func=m.Name("JSONResponse"))):
                    # Add status_code kwarg
                    new_args = list(first.args) + [
                        cst.Arg(
                            keyword=cst.Name("status_code"),
                            value=second,
                        )
                    ]
                    new_call = first.with_changes(args=new_args)
                    return updated.with_changes(value=new_call)

        return updated

    # --- Subscript transforms for session ---

    def leave_Subscript(
        self, original: cst.Subscript, updated: cst.Subscript
    ) -> cst.BaseExpression:
        # session['key'] → request.session['key']
        if m.matches(updated, m.Subscript(value=m.Name("session"))):
            return updated.with_changes(
                value=cst.Attribute(value=cst.Name("request"), attr=cst.Name("session"))
            )
        return updated

    # --- Name transforms for bare session references ---

    def leave_Name(self, original: cst.Name, updated: cst.Name) -> cst.BaseExpression:
        # Bare `session.get(...)` or `session.pop(...)` handled via Attribute
        return updated

    # --- Helpers ---

    def _is_relative_import(self, node: cst.ImportFrom) -> bool:
        """Check if this is a relative import (from . import X)."""
        return len(node.relative) > 0

    def _module_to_str(self, module) -> str:
        if isinstance(module, cst.Name):
            return module.value
        if isinstance(module, cst.Attribute):
            return f"{self._module_to_str(module.value)}.{module.attr.value}"
        if module is None:
            return ""
        return ""

    def _decorator_to_str(self, dec: cst.Decorator) -> str:
        try:
            return cst.parse_module("").code_for_node(dec.decorator)
        except Exception:
            return ""


# ---------------------------------------------------------------------------
# Session.get() attribute transform
# ---------------------------------------------------------------------------

class SessionAttributeTransformer(cst.CSTTransformer):
    """
    Second-pass transformer for session.get() and session.pop().
    Separate from main transformer to avoid conflicts with Subscript handler.
    """

    def leave_Attribute(
        self, original: cst.Attribute, updated: cst.Attribute
    ) -> cst.BaseExpression:
        # session.get → request.session.get
        # session.pop → request.session.pop
        if (
            m.matches(updated, m.Attribute(value=m.Name("session")))
            and isinstance(updated.attr, cst.Name)
            and updated.attr.value in {"get", "pop", "clear", "update", "keys", "values", "items"}
        ):
            return updated.with_changes(
                value=cst.Attribute(value=cst.Name("request"), attr=cst.Name("session"))
            )
        return updated


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def detect_bp_name(source: str) -> str:
    """Detect the blueprint variable name from a routes.py file."""
    tree = cst.parse_module(source)
    for stmt in tree.body:
        if m.matches(stmt, m.SimpleStatementLine()):
            for inner in stmt.body:
                if isinstance(inner, cst.ImportFrom) and len(inner.relative) > 0:
                    names = inner.names
                    if isinstance(names, (list, tuple)):
                        for alias in names:
                            if isinstance(alias.name, cst.Name) and alias.name.value.endswith("_bp"):
                                return alias.name.value
    return "bp"


def transform_routes(source: str, bp_name: str) -> str:
    """Apply all route transforms to a source file."""
    tree = cst.parse_module(source)
    tree = tree.visit(FlaskRouteTransformer(bp_name))
    tree = tree.visit(SessionAttributeTransformer())
    return tree.code


def transform_init(source: str) -> str:
    """Apply blueprint init transforms."""
    tree = cst.parse_module(source)
    transformer = BlueprintInitTransformer()
    tree = tree.visit(transformer)
    return tree.code


def process_file(path: Path, dry_run: bool = False) -> str:
    """Process a single file and return the transformed source."""
    source = path.read_text()

    if path.name == "__init__.py":
        result = transform_init(source)
    else:
        bp_name = detect_bp_name(source)
        result = transform_routes(source, bp_name)

    if dry_run:
        print(f"--- {path} (dry run) ---")
        print(result)
    else:
        path.write_text(result)
        print(f"Transformed: {path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Flask → Starlette codemod")
    parser.add_argument("path", help="File or blueprint directory to transform")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    args = parser.parse_args()

    target = Path(args.path)

    if target.is_dir():
        init_file = target / "__init__.py"
        routes_file = target / "routes.py"
        if init_file.exists():
            process_file(init_file, args.dry_run)
        if routes_file.exists():
            process_file(routes_file, args.dry_run)
    elif target.is_file():
        process_file(target, args.dry_run)
    else:
        print(f"Error: {target} not found", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
