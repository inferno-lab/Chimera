"""
GenAI blueprint.
"""
from app.routing import DecoratorRouter as Router

genai_router = Router(routes=[])

from . import routes
