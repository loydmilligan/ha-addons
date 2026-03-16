"""Sensor platform for Ground Control."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GroundControlCoordinator

_LOGGER = logging.getLogger(__name__)


# Sensor definitions: (key, name, icon, unit)
SENSORS = [
    ("active_count", "Active Tasks", "mdi:play-circle", None),
    ("work_queue_count", "Work Queue", "mdi:playlist-play", None),
    ("total_open", "Total Open", "mdi:format-list-bulleted", None),
    ("completed_count", "Completed", "mdi:check-circle", None),
    ("blocked_count", "Blocked", "mdi:block-helper", None),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ground Control sensors."""
    coordinator: GroundControlCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Add standard count sensors
    for key, name, icon, unit in SENSORS:
        entities.append(GroundControlSensor(coordinator, key, name, icon, unit))

    # Add project sensors dynamically
    if coordinator.data and "stats" in coordinator.data:
        projects = coordinator.data["stats"].get("projects", {})
        for slug, project_data in projects.items():
            # Get project name from state if available
            project_name = slug.replace("-", " ").title()
            if coordinator.data.get("state", {}).get("projects", {}).get(slug):
                project_name = coordinator.data["state"]["projects"][slug].get(
                    "name", project_name
                )

            entities.extend(
                [
                    ProjectStatusSensor(coordinator, slug, project_name),
                    ProjectOpenTasksSensor(coordinator, slug, project_name),
                    ProjectProgressSensor(coordinator, slug, project_name),
                ]
            )

    async_add_entities(entities)


class GroundControlSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Ground Control statistics."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: GroundControlCoordinator,
        key: str,
        name: str,
        icon: str,
        unit: str | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"ground_control_{key}"
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self) -> int:
        """Return the sensor value."""
        if self.coordinator.data and "stats" in self.coordinator.data:
            return self.coordinator.data["stats"].get(self._key, 0)
        return 0


class ProjectStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for project status."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: GroundControlCoordinator, slug: str, name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._slug = slug
        self._attr_name = f"Project {name} Status"
        self._attr_unique_id = f"ground_control_project_{slug}_status"
        self._attr_icon = "mdi:clipboard-text"

    @property
    def native_value(self) -> str:
        """Return the project status."""
        if self.coordinator.data and "stats" in self.coordinator.data:
            projects = self.coordinator.data["stats"].get("projects", {})
            return projects.get(self._slug, {}).get("status", "unknown")
        return "unknown"


class ProjectOpenTasksSensor(CoordinatorEntity, SensorEntity):
    """Sensor for project open task count."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: GroundControlCoordinator, slug: str, name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._slug = slug
        self._attr_name = f"Project {name} Open Tasks"
        self._attr_unique_id = f"ground_control_project_{slug}_open_tasks"
        self._attr_icon = "mdi:format-list-checks"

    @property
    def native_value(self) -> int:
        """Return the open task count."""
        if self.coordinator.data and "stats" in self.coordinator.data:
            projects = self.coordinator.data["stats"].get("projects", {})
            return projects.get(self._slug, {}).get("open_tasks", 0)
        return 0


class ProjectProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for project progress percentage."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    def __init__(
        self, coordinator: GroundControlCoordinator, slug: str, name: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._slug = slug
        self._attr_name = f"Project {name} Progress"
        self._attr_unique_id = f"ground_control_project_{slug}_progress"
        self._attr_icon = "mdi:progress-check"

    @property
    def native_value(self) -> int:
        """Return the progress percentage."""
        if self.coordinator.data and "stats" in self.coordinator.data:
            projects = self.coordinator.data["stats"].get("projects", {})
            return projects.get(self._slug, {}).get("progress", 0)
        return 0
