"""The SMN Weather integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_TRACK_HOME, DOMAIN
from .coordinator import ArgentinaSMNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.WEATHER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SMN from a config entry."""
    # Validate that home location is set if tracking home
    if entry.data.get(CONF_TRACK_HOME, False):
        if hass.config.latitude is None or hass.config.longitude is None:
            _LOGGER.error(
                "No coordinates configured for home location. "
                "Please configure home location in Home Assistant settings."
            )
            return False

    # Create coordinator
    coordinator = ArgentinaSMNDataUpdateCoordinator(hass, entry)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Enable home location tracking if configured
    if entry.data.get(CONF_TRACK_HOME, False):
        coordinator.track_home_location()

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
