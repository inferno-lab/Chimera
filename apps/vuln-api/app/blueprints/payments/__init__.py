"""
Payments blueprint.
"""
from app.routing import DecoratorRouter as Router

payments_router = Router(routes=[])

from . import routes
