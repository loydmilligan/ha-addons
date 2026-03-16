"""Config flow for Ground Control integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_ADDON_URL, DEFAULT_ADDON_URL

_LOGGER = logging.getLogger(__name__)


async def validate_addon_connection(hass: HomeAssistant, addon_url: str) -> bool:
    """Validate we can connect to the addon."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{addon_url.rstrip('/')}/api/version",
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                return response.status == 200
    except aiohttp.ClientError as err:
        _LOGGER.debug("Failed to connect to addon: %s", err)
        return False


class GroundControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ground Control."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            addon_url = user_input[CONF_ADDON_URL].rstrip("/")

            if await validate_addon_connection(self.hass, addon_url):
                # Check if already configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Ground Control",
                    data={CONF_ADDON_URL: addon_url},
                )
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDON_URL, default=DEFAULT_ADDON_URL): str,
                }
            ),
            errors=errors,
        )
