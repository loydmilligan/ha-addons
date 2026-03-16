"""Binary sensor platform for Ground Control."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GroundControlCoordinator

_LOGGER = logging.getLogger(__name__)


# Binary sensor definitions: (key, name, icon)
BINARY_SENSORS = [
    ("has_active", "Has Active Task", "mdi:play-circle"),
    ("has_blocked", "Has Blocked Tasks", "mdi:block-helper"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ground Control binary sensors."""
    coordinator: GroundControlCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        GroundControlBinarySensor(coordinator, key, name, icon)
        for key, name, icon in BINARY_SENSORS
    ]

    async_add_entities(entities)


class GroundControlBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for Ground Control."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GroundControlCoordinator,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"ground_control_{key}"
        self._attr_icon = icon

    @property
    def is_on(self) -> bool:
        """Return true if condition is met."""
        if self.coordinator.data and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get(self._key, False)
        return False
