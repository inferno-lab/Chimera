"""
Checkout blueprint.
"""
from app.routing import DecoratorRouter as Router

checkout_router = Router(routes=[])

from . import routes
