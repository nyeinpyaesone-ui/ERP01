"""Web interface module for ERP01 with performance optimizations."""

from flask import Flask, render_template, jsonify
from config import Config
from utils.performance import cache_response, get_cache_stats, clear_cache


def create_app(config: Config = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Application configuration object.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    if config:
        app.config["SECRET_KEY"] = config.get("SECRET_KEY")
        app.config["DEBUG"] = config.get("DEBUG")

    # Register routes
    from web.routes import main as main_routes

    app.register_blueprint(main_routes.bp)

    # Add performance monitoring endpoints
    @app.route("/api/cache/stats")
    @cache_response(ttl=5)
    def api_cache_stats():
        """Get cache statistics."""
        return jsonify(get_cache_stats())

    @app.route("/api/cache/clear", methods=["POST"])
    def api_cache_clear():
        """Clear the response cache."""
        return jsonify(clear_cache())

    return app
