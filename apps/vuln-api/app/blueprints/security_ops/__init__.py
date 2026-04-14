"""
Security Ops blueprint.
"""
from app.routing import DecoratorRouter as Router

security_ops_router = Router(routes=[])
security_ops_bp = security_ops_router

from . import routes
