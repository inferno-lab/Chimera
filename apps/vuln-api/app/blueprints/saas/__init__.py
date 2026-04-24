"""
SaaS blueprint.
"""
from app.routing import DecoratorRouter as Router

saas_router = Router(routes=[])

from . import routes
