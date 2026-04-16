"""
Mobile blueprint.
"""
from app.routing import DecoratorRouter as Router

mobile_router = Router(routes=[])

from . import routes
