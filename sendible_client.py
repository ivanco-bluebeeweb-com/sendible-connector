"""HTTP client for Sendible REST API v1."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_BASE = "https://api.sendible.com/api/v1"

class SendibleClient:
    def __init__(self, access_token: str, base_url: str = ""):
        self.token = access_token.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Imperal-Sendible-Connector/1.0.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    async def _req(self, method: str, endpoint: str, json: Any = None, params: Any = None) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.request(method, url, headers=self.headers, json=json, params=params)
            if resp.status_code >= 400:
                raise RuntimeError(f"Sendible API error ({resp.status_code}): {resp.text[:300]}")
            if resp.status_code == 204:
                return {}
            return resp.json()

    async def verify_auth(self) -> dict[str, Any]:
        return await self._req("GET", "/profiles.json")

    async def list_profiles(self, limit: int = 20) -> list[dict[str, Any]]:
        res = await self._req("GET", "/profiles.json", params={"limit": limit})
        if isinstance(res, list):
            return res
        return res.get("profiles", res.get("items", []))

    async def get_profile(self, profile_id: str) -> dict[str, Any]:
        return await self._req("GET", f"/profiles/{profile_id}.json")

    async def list_messages(self, status: str = "scheduled", limit: int = 20) -> list[dict[str, Any]]:
        endpoint = f"/messages/{status}.json"
        res = await self._req("GET", endpoint, params={"limit": limit})
        if isinstance(res, list):
            return res
        return res.get("messages", res.get("items", []))

    async def get_message(self, message_id: str) -> dict[str, Any]:
        return await self._req("GET", f"/messages/{message_id}.json")

    async def create_message(self, content: str, profile_ids: list[str], scheduled_for: Optional[str] = None, image_url: Optional[str] = None) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "content": content,
            "profiles": profile_ids
        }
        if scheduled_for:
            payload["scheduled_for"] = scheduled_for
        if image_url:
            payload["image_url"] = image_url
        return await self._req("POST", "/messages.json", json=payload)

    async def update_message(self, message_id: str, content: Optional[str] = None, scheduled_for: Optional[str] = None) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if content is not None:
            payload["content"] = content
        if scheduled_for is not None:
            payload["scheduled_for"] = scheduled_for
        return await self._req("PUT", f"/messages/{message_id}.json", json=payload)

    async def delete_message(self, message_id: str) -> dict[str, Any]:
        return await self._req("DELETE", f"/messages/{message_id}.json")

    async def list_activities(self, limit: int = 20) -> list[dict[str, Any]]:
        res = await self._req("GET", "/activities.json", params={"limit": limit})
        if isinstance(res, list):
            return res
        return res.get("activities", res.get("items", []))
