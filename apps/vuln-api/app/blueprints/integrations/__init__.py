"""
Integrations blueprint.
"""
from app.routing import DecoratorRouter as Router

integrations_router = Router(routes=[])

from . import routes
