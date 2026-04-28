"""
Ecommerce blueprint.
"""
from app.routing import DecoratorRouter as Router

ecommerce_router = Router(routes=[])

from . import routes
