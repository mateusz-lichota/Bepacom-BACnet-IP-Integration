"""The Bepacom EcoPanel BACnet/IP integration."""

from __future__ import annotations

from asyncio import sleep
from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ENABLED,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
)
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry

from .const import (
    ATTR_INDEX,
    ATTR_PRIORITY,
    ATTR_PROPERTY,
    ATTR_VALUE,
    DOMAIN,
    LOGGER,
    WRITE_PROPERTY_SCHEMA,
    WRITE_PROPERTY_SERVICE_NAME,
    WRITE_RELEASE_SCHEMA,
    WRITE_RELEASE_SERVICE_NAME,
)
from .coordinator import EcoPanelDataUpdateCoordinator

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = [
    "binary_sensor",
    "sensor",
    "number",
    "switch",
    "select",
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up EcoPanel BACnet/IP interface from a config entry."""

    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.

    # entry = validate_entry(entry)

    coordinator = EcoPanelDataUpdateCoordinator(hass, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload entry when its updated.
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    entry.async_create_background_task(
        hass,
        async_monitor_data_size(hass, entry, coordinator),
        name="bacnet-monitor-data",
    )

    async def write_release(call: ServiceCall) -> ServiceResponse:
        """Write empty presentValue that serves to release higher priority write request."""

        entity_registry = er.async_get(hass)

        entity_data = entity_registry.async_get(call.data[ATTR_ENTITY_ID][0])
        assert entity_data is not None

        device_id, object_id = entity_data.unique_id.split("_")

        if call.data.get(ATTR_PRIORITY):
            LOGGER.warning(
                "Priority is currently not functioning. Writing default value."
            )

        await coordinator.interface.write_property(
            deviceid=device_id, objectid=object_id
        )

        return {"status": "successfull!"}

    async def write_property(call: ServiceCall) -> ServiceResponse:
        """Write property with value to an object."""

        entity_registry = er.async_get(hass)

        entity_data = entity_registry.async_get(call.data[ATTR_ENTITY_ID][0])
        assert entity_data is not None

        device_id, object_id = entity_data.unique_id.split("_")

        if priority := call.data.get(ATTR_PRIORITY):
            pass

        if property_id := call.data.get(ATTR_PROPERTY):
            pass

        if value := call.data.get(ATTR_VALUE):
            pass

        if array_index := call.data.get(ATTR_INDEX):
            pass

        await coordinator.interface.write_property_v2(
            deviceid=device_id,
            objectid=object_id,
            propertyid=property_id,
            value=value,
            array_index=array_index,
            priority=priority,
        )

        return {"status": "successfull!"}

    hass.services.async_register(
        DOMAIN,
        WRITE_RELEASE_SERVICE_NAME,
        write_release,
        schema=WRITE_RELEASE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        WRITE_PROPERTY_SERVICE_NAME,
        write_property,
        schema=WRITE_PROPERTY_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )

    return True


def validate_entry(entry: ConfigEntry) -> ConfigEntry:
    """Check if all values are filled in, otherwise replace"""

    entry_data = cast(dict[str, Any], entry.data)

    if not entry.data.get(CONF_PORT):
        entry_data.update({CONF_PORT: 8099})

    if not entry.data.get(CONF_ENABLED):
        entry_data.update({CONF_ENABLED: True})

    if not entry.data.get(CONF_HOST):
        entry_data.update({CONF_HOST: "127.0.0.1"})

    if not entry.data.get(CONF_NAME):
        entry_data.update({CONF_NAME: "object_name"})

    return entry


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: EcoPanelDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

        await coordinator.interface.disconnect()
        if coordinator.unsub:
            coordinator.unsub()

        del hass.data[DOMAIN][entry.entry_id]

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove config entry from a device."""
    coordinator: EcoPanelDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    for _domain, device_id in device_entry.identifiers:
        try:
            coordinator.logger.info(
                f"(Removing device {coordinator.data.devices.get(device_id)}"
            )
            coordinator.data.devices.pop(device_id)
        except KeyError:
            continue

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when it changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_monitor_data_size(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: EcoPanelDataUpdateCoordinator,
    reload_period_seconds: int = 30,
) -> None:
    """Monitor data size, and reload if it increases."""

    num_old_devices = len(coordinator.data.devices)
    old_device_sizes = {
        device: len(coordinator.data.devices[device].objects)
        for device in coordinator.data.devices
    }
    while True:
        await sleep(reload_period_seconds)

        if len(coordinator.data.devices) > num_old_devices:
            LOGGER.debug("Reloading after new device detected!")

            hass.config_entries.async_schedule_reload(entry.entry_id)

        for device_name, device in coordinator.data.devices.items():
            if len(device.objects) > old_device_sizes.get(device_name, 0):
                LOGGER.debug("Increased object size")

                hass.config_entries.async_schedule_reload(entry.entry_id)
