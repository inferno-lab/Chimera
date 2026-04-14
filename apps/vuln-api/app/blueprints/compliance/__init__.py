"""
Compliance blueprint.
"""
from app.routing import DecoratorRouter as Router

compliance_router = Router(routes=[])
compliance_bp = compliance_router

from . import routes
