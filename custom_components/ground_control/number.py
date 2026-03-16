"""Number platform for Ground Control configuration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, UPDATE_INTERVAL
from .coordinator import GroundControlCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ground Control number entities."""
    coordinator: GroundControlCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        RefreshIntervalNumber(coordinator, entry),
    ])


class RefreshIntervalNumber(NumberEntity):
    """Number entity for refresh interval configuration."""

    _attr_has_entity_name = True
    _attr_name = "Refresh Interval"
    _attr_unique_id = "ground_control_refresh_interval"
    _attr_icon = "mdi:refresh"
    _attr_native_min_value = 5
    _attr_native_max_value = 300
    _attr_native_step = 5
    _attr_native_unit_of_measurement = "seconds"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: GroundControlCoordinator, entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        self._coordinator = coordinator
        self._entry = entry
        self._attr_native_value = entry.options.get("refresh_interval", UPDATE_INTERVAL)

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._entry.options.get("refresh_interval", UPDATE_INTERVAL)

    async def async_set_native_value(self, value: float) -> None:
        """Update the refresh interval."""
        new_options = dict(self._entry.options)
        new_options["refresh_interval"] = int(value)
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)

        # Update coordinator interval
        from datetime import timedelta
        self._coordinator.update_interval = timedelta(seconds=int(value))
        _LOGGER.info(f"Refresh interval updated to {int(value)} seconds")

        # Request immediate refresh
        await self._coordinator.async_request_refresh()
