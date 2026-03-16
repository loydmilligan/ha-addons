"""Ground Control integration for Home Assistant."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_ADDON_URL, UPDATE_INTERVAL
from .coordinator import GroundControlCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER]

# Service schemas
SERVICE_CREATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("subject"): cv.string,
        vol.Optional("description", default=""): cv.string,
        vol.Optional("bucket", default="brainstorm"): cv.string,
        vol.Optional("project", default=""): cv.string,
    }
)

SERVICE_UPDATE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Optional("subject"): cv.string,
        vol.Optional("description"): cv.string,
        vol.Optional("bucket"): cv.string,
        vol.Optional("project"): cv.string,
    }
)

SERVICE_MOVE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
        vol.Required("target_bucket"): cv.string,
    }
)

SERVICE_TASK_ID_SCHEMA = vol.Schema(
    {
        vol.Required("task_id"): cv.string,
    }
)

SERVICE_CREATE_PROJECT_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("goal"): cv.string,
        vol.Optional("description", default=""): cv.string,
    }
)

SERVICE_UPDATE_PROJECT_SCHEMA = vol.Schema(
    {
        vol.Required("slug"): cv.string,
        vol.Optional("status"): cv.string,
        vol.Optional("goal"): cv.string,
        vol.Optional("name"): cv.string,
    }
)

SERVICE_PROJECT_SLUG_SCHEMA = vol.Schema(
    {
        vol.Required("slug"): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ground Control from a config entry."""
    addon_url = entry.data[CONF_ADDON_URL]
    refresh_interval = entry.options.get("refresh_interval", UPDATE_INTERVAL)

    coordinator = GroundControlCoordinator(hass, addon_url, refresh_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    await _async_setup_services(hass, coordinator)

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_options_updated))

    return True


async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator: GroundControlCoordinator = hass.data[DOMAIN][entry.entry_id]
    refresh_interval = entry.options.get("refresh_interval", UPDATE_INTERVAL)

    from datetime import timedelta
    coordinator.update_interval = timedelta(seconds=refresh_interval)
    _LOGGER.info(f"Options updated: refresh_interval={refresh_interval}s")

    await coordinator.async_request_refresh()


async def _async_setup_services(
    hass: HomeAssistant, coordinator: GroundControlCoordinator
) -> None:
    """Set up Ground Control services."""

    async def handle_create_task(call: ServiceCall) -> None:
        """Handle create_task service call."""
        await coordinator.async_call_service(
            "POST",
            "/api/tasks",
            {
                "subject": call.data["subject"],
                "description": call.data.get("description", ""),
                "bucket": call.data.get("bucket", "brainstorm"),
                "project": call.data.get("project", ""),
            },
        )
        await coordinator.async_request_refresh()

    async def handle_update_task(call: ServiceCall) -> None:
        """Handle update_task service call."""
        task_id = call.data["task_id"].upper()
        update_data = {}
        for field in ["subject", "description", "bucket", "project"]:
            if field in call.data:
                update_data[field] = call.data[field]

        await coordinator.async_call_service("PUT", f"/api/tasks/{task_id}", update_data)
        await coordinator.async_request_refresh()

    async def handle_move_task(call: ServiceCall) -> None:
        """Handle move_task service call."""
        task_id = call.data["task_id"].upper()
        await coordinator.async_call_service(
            "POST",
            f"/api/tasks/{task_id}/move",
            {"bucket": call.data["target_bucket"]},
        )
        await coordinator.async_request_refresh()

    async def handle_complete_task(call: ServiceCall) -> None:
        """Handle complete_task service call."""
        task_id = call.data["task_id"].upper()
        await coordinator.async_call_service("POST", f"/api/tasks/{task_id}/complete", {})
        await coordinator.async_request_refresh()

    async def handle_delete_task(call: ServiceCall) -> None:
        """Handle delete_task service call."""
        task_id = call.data["task_id"].upper()
        await coordinator.async_call_service("DELETE", f"/api/tasks/{task_id}", None)
        await coordinator.async_request_refresh()

    async def handle_create_project(call: ServiceCall) -> None:
        """Handle create_project service call."""
        await coordinator.async_call_service(
            "POST",
            "/api/projects",
            {
                "name": call.data["name"],
                "goal": call.data["goal"],
                "description": call.data.get("description", ""),
            },
        )
        await coordinator.async_request_refresh()

    async def handle_update_project(call: ServiceCall) -> None:
        """Handle update_project service call."""
        slug = call.data["slug"]
        update_data = {}
        for field in ["status", "goal", "name"]:
            if field in call.data:
                update_data[field] = call.data[field]

        await coordinator.async_call_service("PUT", f"/api/projects/{slug}", update_data)
        await coordinator.async_request_refresh()

    async def handle_archive_project(call: ServiceCall) -> None:
        """Handle archive_project service call."""
        slug = call.data["slug"]
        await coordinator.async_call_service("DELETE", f"/api/projects/{slug}", None)
        await coordinator.async_request_refresh()

    # Register all services
    hass.services.async_register(
        DOMAIN, "create_task", handle_create_task, SERVICE_CREATE_TASK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "update_task", handle_update_task, SERVICE_UPDATE_TASK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "move_task", handle_move_task, SERVICE_MOVE_TASK_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "complete_task", handle_complete_task, SERVICE_TASK_ID_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "delete_task", handle_delete_task, SERVICE_TASK_ID_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "create_project", handle_create_project, SERVICE_CREATE_PROJECT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "update_project", handle_update_project, SERVICE_UPDATE_PROJECT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, "archive_project", handle_archive_project, SERVICE_PROJECT_SLUG_SCHEMA
    )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
    return unload_ok
