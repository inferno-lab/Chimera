"""
Healthcare blueprint.
"""
from app.routing import DecoratorRouter as Router

healthcare_router = Router(routes=[])

from . import routes
