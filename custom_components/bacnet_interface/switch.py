from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (SwitchDeviceClass, SwitchEntity,
                                             SwitchEntityDescription)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (CONF_ENABLED, CONF_NAME, DATA_BYTES,
                                 ELECTRIC_CURRENT_MILLIAMPERE, PERCENTAGE,
                                 SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
                                 UnitOfTemperature)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import utcnow

from .const import DOMAIN, LOGGER
from .coordinator import EcoPanelDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoPanel sensor based on a config entry."""
    coordinator: EcoPanelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entity_list: list = []

    # Collect from all devices the objects that can become a sensor
    for deviceid in coordinator.data.devices:
        for objectid in coordinator.data.devices[deviceid].objects:
            if (
                coordinator.data.devices[deviceid].objects[objectid].objectIdentifier[0]
                == "binaryValue"
            ):
                entity_list.append(
                    BinaryValueEntity(
                        coordinator=coordinator, deviceid=deviceid, objectid=objectid
                    )
                )
            elif (
                coordinator.data.devices[deviceid].objects[objectid].objectIdentifier[0]
                == "binaryOutput"
            ):
                entity_list.append(
                    BinaryOutputEntity(
                        coordinator=coordinator, deviceid=deviceid, objectid=objectid
                    )
                )
    async_add_entities(entity_list)


class BinaryValueEntity(CoordinatorEntity[EcoPanelDataUpdateCoordinator], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoPanelDataUpdateCoordinator,
        deviceid: str,
        objectid: str,
    ):
        """Initialize a BACnet BinaryValue object as entity."""
        super().__init__(coordinator=coordinator)
        self.deviceid = deviceid
        self.objectid = objectid

    @property
    def unique_id(self) -> str:
        return f"{self.deviceid}_{self.objectid}"

    @property
    def name(self) -> str:
        name = self.coordinator.config_entry.data.get(CONF_NAME, "object_name")
        if name == "description":
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].description}"
        else:
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].objectName}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.coordinator.config_entry.data.get(CONF_ENABLED, False)

    @property
    def is_on(self) -> bool:
        if (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
            == "active"
        ):
            return True
        elif (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
            == "inactive"
        ):
            return False

    @property
    def icon(self):
        return "mdi:lightbulb-outline"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.deviceid)},
            name=f"{self.coordinator.data.devices[self.deviceid].objects[self.deviceid].objectName}",
            manufacturer=self.coordinator.data.devices[self.deviceid]
            .objects[self.deviceid]
            .vendorName,
            model=self.coordinator.data.devices[self.deviceid]
            .objects[self.deviceid]
            .modelName,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "OutOfService": self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .outOfService,
            "EventState": self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .eventState,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set BinaryValue object to active"""
        await self.coordinator.interface.write_property(
            deviceid=self.deviceid, objectid=self.objectid, presentValue="1"
        )

    async def async_turn_off(self):
        """Set BinaryValue object to active."""
        await self.coordinator.interface.write_property(
            deviceid=self.deviceid, objectid=self.objectid, presentValue="0"
        )


class BinaryOutputEntity(
    CoordinatorEntity[EcoPanelDataUpdateCoordinator], SwitchEntity
):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoPanelDataUpdateCoordinator,
        deviceid: str,
        objectid: str,
    ):
        """Initialize a BACnet BinaryOutput object as entity."""
        super().__init__(coordinator=coordinator)
        self.deviceid = deviceid
        self.objectid = objectid

    @property
    def unique_id(self) -> str:
        return f"{self.deviceid}_{self.objectid}"

    @property
    def name(self) -> str:
        name = self.coordinator.config_entry.data.get(CONF_NAME, "object_name")
        if name == "description":
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].description}"
        else:
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].objectName}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.coordinator.config_entry.data.get(CONF_ENABLED, False)

    @property
    def is_on(self) -> bool:
        if (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
            == "active"
        ):
            return True
        elif (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
            == "inactive"
        ):
            return False

    @property
    def icon(self):
        return "mdi:lightbulb-outline"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.deviceid)},
            name=f"{self.coordinator.data.devices[self.deviceid].objects[self.deviceid].objectName}",
            manufacturer=self.coordinator.data.devices[self.deviceid]
            .objects[self.deviceid]
            .vendorName,
            model=self.coordinator.data.devices[self.deviceid]
            .objects[self.deviceid]
            .modelName,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "OutOfService": self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .outOfService,
            "EventState": self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .eventState,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Set BinaryValue object to active"""
        await self.coordinator.interface.write_property(
            deviceid=self.deviceid, objectid=self.objectid, presentValue="1"
        )

    async def async_turn_off(self):
        """Set BinaryValue object to active."""
        await self.coordinator.interface.write_property(
            deviceid=self.deviceid, objectid=self.objectid, presentValue="0"
        )
