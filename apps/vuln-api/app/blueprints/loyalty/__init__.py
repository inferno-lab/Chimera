"""
Loyalty blueprint.
"""
from app.routing import DecoratorRouter as Router

loyalty_router = Router(routes=[])
loyalty_bp = loyalty_router

from . import routes
