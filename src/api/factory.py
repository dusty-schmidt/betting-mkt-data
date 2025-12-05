# src/api/factory.py
"""Factory to create the Flask application.

The function ``create_app`` sets up the Flask instance, registers the API blueprint,
and can be extended with additional configuration (e.g., CORS, logging).
"""

from flask import Flask
from .routes import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    # Register API blueprint
    app.register_blueprint(api_bp)
    # Additional configuration can go here
    return app
