"""Main routes for the web interface with performance optimizations."""

from flask import Blueprint, render_template, jsonify
from utils.performance import cache_response, performance_monitor

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Render the main dashboard page."""
    return render_template("index.html")


@bp.route("/api/status")
@cache_response(ttl=30)  # Cache status for 30 seconds
@performance_monitor
def api_status():
    """Return API status information."""
    return jsonify(
        {
            "status": "online",
            "version": "1.0.0",
            "message": "ERP01 Web Interface is running",
        }
    )


@bp.route("/health")
@cache_response(ttl=10)  # Cache health check for 10 seconds
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({"healthy": True, "status": "ok"})


@bp.route("/api/modules")
@cache_response(ttl=60)  # Cache modules list for 60 seconds
@performance_monitor
def api_modules():
    """Return available modules information."""
    return jsonify(
        {
            "modules": [
                {"id": 1, "name": "Dashboard", "status": "active"},
                {"id": 2, "name": "Inventory", "status": "active"},
                {"id": 3, "name": "Finance", "status": "active"},
                {"id": 4, "name": "HR", "status": "pending"},
            ]
        }
    )


@bp.route("/api/modules/<int:module_id>")
@cache_response(ttl=120)  # Cache module details for 2 minutes
def api_module_detail(module_id):
    """Return details for a specific module."""
    modules = {
        1: {
            "id": 1,
            "name": "Dashboard",
            "status": "active",
            "description": "Main dashboard",
        },
        2: {
            "id": 2,
            "name": "Inventory",
            "status": "active",
            "description": "Inventory management",
        },
        3: {
            "id": 3,
            "name": "Finance",
            "status": "active",
            "description": "Financial operations",
        },
        4: {
            "id": 4,
            "name": "HR",
            "status": "pending",
            "description": "Human resources",
        },
    }

    if module_id in modules:
        return jsonify(modules[module_id])
    return jsonify({"error": "Module not found"}), 404
