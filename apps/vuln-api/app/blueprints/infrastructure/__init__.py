"""
Infrastructure blueprint.
"""
from app.routing import DecoratorRouter as Router

infrastructure_router = Router(routes=[])

from . import routes
