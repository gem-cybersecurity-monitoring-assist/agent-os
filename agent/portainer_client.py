from __future__ import annotations

from typing import Any

import requests

from config import settings


class PortainerClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or settings.portainer_url).rstrip("/")
        self.api_key = api_key or settings.portainer_api_key
        self.timeout = settings.portainer_timeout_seconds

    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key}

    def _require_config(self) -> None:
        if not self.base_url or not self.api_key or self.api_key == "replace_me":
            raise RuntimeError("PORTAINER_URL and PORTAINER_API_KEY must be configured")

    def _get(self, path: str) -> Any:
        self._require_config()
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_stacks(self) -> list[dict[str, Any]]:
        return self._get("/api/stacks")

    def list_endpoints(self) -> list[dict[str, Any]]:
        return self._get("/api/endpoints")

    def get_stack(self, stack_id: int) -> dict[str, Any]:
        return self._get(f"/api/stacks/{stack_id}")
