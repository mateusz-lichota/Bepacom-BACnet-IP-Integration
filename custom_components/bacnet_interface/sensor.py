from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import DEVICE_CLASS_UNITS
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENABLED, CONF_NAME, UnitOfEnergy, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import STATETEXT_OFFSET
from .const import DOMAIN, LOGGER
from .coordinator import EcoPanelDataUpdateCoordinator
from .helper import bacnet_to_device_class, bacnet_to_ha_units, decimal_places_needed


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EcoPanel sensor based on a config entry."""
    coordinator: EcoPanelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entity_list: list[Entity] = []

    # Collect from all devices the objects that can become a sensor
    for deviceid in coordinator.data.devices:
        if not coordinator.data.devices[deviceid].objects:
            LOGGER.warning(f"No objects in {deviceid}!")
            continue

        for objectid in coordinator.data.devices[deviceid].objects:
            if (
                not coordinator.data.devices[deviceid]
                .objects[objectid]
                .objectIdentifier
            ):
                LOGGER.warning(f"No object identifier for {objectid} in {deviceid}!")
                continue

            if (
                coordinator.data.devices[deviceid].objects[objectid].objectIdentifier[0]
                == "analogInput"
            ):
                entity_list.append(
                    AnalogInputEntity(
                        coordinator=coordinator, deviceid=deviceid, objectid=objectid
                    )
                )
            # elif coordinator.data.devices[deviceid].objects[objectid].objectType == 'accumulator':
            #    entity_list.append(AnalogInputEntity(coordinator=coordinator, deviceid=deviceid, objectid=objectid))
            # elif coordinator.data.devices[deviceid].objects[objectid].objectType == 'averaging':
            #    entity_list.append(AveragingEntity(coordinator=coordinator, deviceid=deviceid, objectid=objectid))
            elif (
                coordinator.data.devices[deviceid].objects[objectid].objectIdentifier[0]
                == "multiStateInput"
            ):
                entity_list.append(
                    MultiStateInputEntity(
                        coordinator=coordinator, deviceid=deviceid, objectid=objectid
                    )
                )

    async_add_entities(entity_list)


class AnalogInputEntity(CoordinatorEntity[EcoPanelDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoPanelDataUpdateCoordinator,
        deviceid: str,
        objectid: str,
    ):
        """Initialize a BACnet AnalogInput object as entity."""
        super().__init__(coordinator=coordinator)
        self.deviceid = deviceid
        self.objectid = objectid

    @property
    def unique_id(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        return f"{self.deviceid}_{self.objectid}"

    @property
    def name(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        name = self.coordinator.config_entry.data.get(CONF_NAME, "object_name")
        if name == "description":
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].description}"
        elif name == "object_identifier":
            identifier = (
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .objectIdentifier
            )
            return f"{identifier[0]}:{identifier[1]}"
        else:
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].objectName}"

    @property
    def entity_registry_enabled_default(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.coordinator.config_entry.data.get(CONF_ENABLED, False)

    @property
    def native_value(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        value = (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
        )

        if (
            resolution := self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .resolution
        ):
            if resolution >= 1:
                return int(value)
            resolution = decimal_places_needed(resolution)
            return round(value, resolution)
        elif (
            covIncrement := self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .covIncrement
        ):
            if covIncrement >= 1:
                return int(value)
            covIncrement = decimal_places_needed(covIncrement)
            return round(value, covIncrement)

        return round(value, 1)

    @property
    def icon(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "mdi:gauge"

    @property
    def device_class(self) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if (
            units := self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .units
        ):
            # device_class_units = cast(
            #     Mapping[str, Collection[str | type[StrEnum] | None]], DEVICE_CLASS_UNITS
            # )
            return bacnet_to_device_class(units, DEVICE_CLASS_UNITS)
        else:
            return None

    @property
    def native_unit_of_measurement(self) -> str | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if (
            units := self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .units
        ):
            return bacnet_to_ha_units(units)
        else:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return {
            "inAlarm": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[0]
            ),
            "fault": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[1]
            ),
            "overridden": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[2]
            ),
            "outOfService": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[3]
            ),
        }

    @property
    def device_info(self) -> DeviceInfo:  # pyright: ignore[reportIncompatibleMethodOverride]
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
    def state_class(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        if self.native_unit_of_measurement in UnitOfEnergy:
            return "total"
        elif self.native_unit_of_measurement in UnitOfVolume:
            return "total"
        else:
            return "measurement"


class MultiStateInputEntity(
    CoordinatorEntity[EcoPanelDataUpdateCoordinator], SensorEntity
):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EcoPanelDataUpdateCoordinator,
        deviceid: str,
        objectid: str,
    ):
        """Initialize a BACnet MultiStateInput object as entity."""
        super().__init__(coordinator=coordinator)
        self.deviceid = deviceid
        self.objectid = objectid

    @property
    def unique_id(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        return f"{self.deviceid}_{self.objectid}"

    @property
    def name(self) -> str:  # pyright: ignore[reportIncompatibleMethodOverride]
        name = self.coordinator.config_entry.data.get(CONF_NAME, "object_name")
        if name == "description":
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].description}"
        elif name == "object_identifier":
            identifier = (
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .objectIdentifier
            )
            return f"{identifier[0]}:{identifier[1]}"
        else:
            return f"{self.coordinator.data.devices[self.deviceid].objects[self.objectid].objectName}"

    @property
    def entity_registry_enabled_default(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.coordinator.config_entry.data.get(CONF_ENABLED, False)

    @property
    def native_value(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        state_val = (
            self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .presentValue
        )

        if (
            state_text := self.coordinator.data.devices[self.deviceid]
            .objects[self.objectid]
            .stateText
        ):
            return state_text[state_val - STATETEXT_OFFSET]  # JCO
        else:
            return state_val

    @property
    def icon(self):  # pyright: ignore[reportIncompatibleMethodOverride]
        return "mdi:menu"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return {
            "inAlarm": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[0]
            ),
            "fault": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[1]
            ),
            "overridden": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[2]
            ),
            "outOfService": bool(
                self.coordinator.data.devices[self.deviceid]
                .objects[self.objectid]
                .statusFlags[3]
            ),
        }

    @property
    def device_info(self) -> DeviceInfo:  # pyright: ignore[reportIncompatibleMethodOverride]
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
