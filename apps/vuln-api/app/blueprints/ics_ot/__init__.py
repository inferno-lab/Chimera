"""
Ics Ot blueprint.
"""
from app.routing import DecoratorRouter as Router

ics_ot_router = Router(routes=[])

from . import routes
