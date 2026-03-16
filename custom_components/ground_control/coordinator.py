"""DataUpdateCoordinator for Ground Control."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class GroundControlCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch data from Ground Control addon."""

    def __init__(self, hass: HomeAssistant, addon_url: str, refresh_interval: int = UPDATE_INTERVAL) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=refresh_interval),
        )
        self.addon_url = addon_url.rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from addon API."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

        try:
            # Fetch stats endpoint
            async with self._session.get(
                f"{self.addon_url}/api/stats",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"API /api/stats returned {response.status}")
                stats = await response.json()

            # Fetch full state for additional details
            async with self._session.get(
                f"{self.addon_url}/api/tasks",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(f"API /api/tasks returned {response.status}")
                state = await response.json()

            return {
                "stats": stats,
                "state": state,
            }

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with addon: {err}") from err

    async def async_close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def async_call_service(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Call an addon API endpoint."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

        url = f"{self.addon_url}{endpoint}"
        try:
            if method == "POST":
                async with self._session.post(
                    url, json=data, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    if response.status >= 400:
                        raise UpdateFailed(f"API error: {result.get('error', 'Unknown')}")
                    return result
            elif method == "PUT":
                async with self._session.put(
                    url, json=data, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    if response.status >= 400:
                        raise UpdateFailed(f"API error: {result.get('error', 'Unknown')}")
                    return result
            elif method == "DELETE":
                async with self._session.delete(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    if response.status >= 400:
                        raise UpdateFailed(f"API error: {result.get('error', 'Unknown')}")
                    return result
            else:
                raise ValueError(f"Unsupported method: {method}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error calling addon API: {err}") from err
