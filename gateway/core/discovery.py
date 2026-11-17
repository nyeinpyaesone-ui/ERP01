"""Static, deployment-controlled service registry.

No request parameter can register a URL. This prevents an untrusted caller from
turning the gateway into an SSRF proxy.
"""

import logging
import os
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

MODULE_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,39}$")


@dataclass(frozen=True)
class ServiceEndpoint:
    name: str
    base_url: str
    health_url: str


class ServiceRegistry:
    def __init__(self, enabled_modules: list[str] | None = None):
        self._services: dict[str, ServiceEndpoint] = {}
        self._enabled_modules = enabled_modules or []

    @staticmethod
    def _validate_url(name: str, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(f"Invalid upstream URL configured for module '{name}'.")
        path_segments = parsed.path.split("/")
        if any(segment in {".", ".."} for segment in path_segments):
            raise ValueError(f"Unsafe upstream path configured for module '{name}'.")
        return value.rstrip("/")

    def load_from_environment(self) -> None:
        configured: dict[str, ServiceEndpoint] = {}
        for name in self._enabled_modules:
            if not MODULE_NAME.fullmatch(name):
                logger.warning("Ignoring invalid module identifier in MODULES_ENABLED.")
                continue

            raw_url = os.getenv(f"SERVICE_{name.upper()}_URL")
            if not raw_url:
                logger.warning("Module '%s' is enabled but has no service URL.", name)
                continue

            base_url = self._validate_url(name, raw_url)
            raw_health_url = os.getenv(f"SERVICE_{name.upper()}_HEALTH_URL")
            health_url = (
                self._validate_url(name, raw_health_url)
                if raw_health_url
                else base_url + "/health"
            )
            configured[name] = ServiceEndpoint(
                name=name,
                base_url=base_url,
                health_url=health_url,
            )

        self._services = configured

    def get(self, name: str) -> ServiceEndpoint | None:
        return self._services.get(name.lower())

    def get_all(self) -> dict[str, ServiceEndpoint]:
        return dict(self._services)

    def public_status(self) -> list[dict[str, str]]:
        return [
            {"name": name, "configured": "true"}
            for name in sorted(self._services)
        ]
