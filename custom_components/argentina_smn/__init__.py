"""The SMN Weather integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import ALERT_EVENT_MAP, ALERT_LEVEL_MAP, CONF_TRACK_HOME, DOMAIN
from .coordinator import ArgentinaSMNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.WEATHER, Platform.BINARY_SENSOR]

# Service names
SERVICE_GET_ALERTS = "get_alerts"
SERVICE_GET_ALERTS_FOR_LOCATION = "get_alerts_for_location"

# Service schemas
SERVICE_GET_ALERTS_SCHEMA = vol.Schema(
    {
        vol.Optional("config_entry_id"): cv.string,
    }
)

SERVICE_GET_ALERTS_FOR_LOCATION_SCHEMA = vol.Schema(
    {
        vol.Required("location_id"): cv.string,
    }
)


def _parse_alerts(alerts_data: dict[str, Any]) -> dict[str, Any]:
    """Parse raw alerts data into structured format for automations."""
    if not alerts_data or not isinstance(alerts_data, dict):
        return {"active_alerts": [], "max_severity": "info", "area_id": None}

    warnings = alerts_data.get("warnings", [])
    reports = alerts_data.get("reports", [])
    area_id = alerts_data.get("area_id")

    active_alerts = []
    max_severity_level = 1

    # Get current day's warnings
    if warnings and len(warnings) > 0:
        current_warning = warnings[0]
        events = current_warning.get("events", [])

        for event in events:
            event_id = event.get("id")
            max_level = event.get("max_level", 1)

            # Skip level 1 (no alert)
            if max_level <= 1:
                continue

            # Track max severity
            max_severity_level = max(max_severity_level, max_level)

            # Get event name
            event_name = ALERT_EVENT_MAP.get(event_id, f"unknown_{event_id}")

            # Get level info
            level_info = ALERT_LEVEL_MAP.get(max_level, ALERT_LEVEL_MAP[1])

            # Find report for this event
            description = None
            instruction = None
            for report in reports:
                if report.get("event_id") == event_id:
                    levels = report.get("levels", [])
                    for level_data in levels:
                        if level_data.get("level") == max_level:
                            description = level_data.get("description")
                            instruction = level_data.get("instruction")
                            break

            active_alerts.append({
                "event_id": event_id,
                "event_name": event_name,
                "max_level": max_level,
                "level_name": level_info["name"],
                "color": level_info["color"],
                "severity": level_info["severity"],
                "date": current_warning.get("date"),
                "description": description,
                "instruction": instruction,
            })

    # Get overall max severity
    max_severity_info = ALERT_LEVEL_MAP.get(max_severity_level, ALERT_LEVEL_MAP[1])

    return {
        "active_alerts": active_alerts,
        "max_severity": max_severity_info["severity"],
        "max_level": max_severity_level,
        "area_id": area_id,
        "updated": alerts_data.get("updated"),
    }


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

    # Register services (only once)
    if not hass.services.has_service(DOMAIN, SERVICE_GET_ALERTS):
        async def handle_get_alerts(call: ServiceCall) -> dict[str, Any]:
            """Handle get_alerts service call."""
            config_entry_id = call.data.get("config_entry_id")

            # If no config_entry_id provided, use the first one
            if not config_entry_id:
                if hass.data.get(DOMAIN):
                    config_entry_id = next(iter(hass.data[DOMAIN]))
                else:
                    _LOGGER.error("No SMN integration configured")
                    return {"active_alerts": [], "max_severity": "info", "area_id": None}

            # Get coordinator
            coordinator = hass.data[DOMAIN].get(config_entry_id)
            if not coordinator:
                _LOGGER.warning(
                    "Invalid config_entry_id: %s. Use the integration's config entry ID, not location ID. "
                    "Leave empty to use the default integration.",
                    config_entry_id
                )
                return {"active_alerts": [], "max_severity": "info", "area_id": None}

            # Parse and return alerts
            result = _parse_alerts(coordinator.data.alerts)
            _LOGGER.info(
                "Alerts service called: found %d active alerts with max severity '%s'",
                len(result.get("active_alerts", [])),
                result.get("max_severity", "info")
            )
            return result

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ALERTS,
            handle_get_alerts,
            schema=SERVICE_GET_ALERTS_SCHEMA,
            supports_response="only",
        )

    # Register get_alerts_for_location service (only once)
    if not hass.services.has_service(DOMAIN, SERVICE_GET_ALERTS_FOR_LOCATION):
        async def handle_get_alerts_for_location(call: ServiceCall) -> dict[str, Any]:
            """Handle get_alerts_for_location service call."""
            location_id = call.data.get("location_id")

            # Get token manager from first available coordinator
            if not hass.data.get(DOMAIN):
                _LOGGER.error("No SMN integration configured. Set up integration first.")
                return {"active_alerts": [], "max_severity": "info", "area_id": None}

            # Get first coordinator to access token manager
            first_entry_id = next(iter(hass.data[DOMAIN]))
            coordinator = hass.data[DOMAIN][first_entry_id]

            # Fetch alerts directly from API
            try:
                import aiohttp
                import async_timeout
                from .const import API_ALERT_ENDPOINT

                token = await coordinator._smn_data._token_manager.get_token()
                headers = {
                    "Authorization": f"JWT {token}",
                    "Accept": "application/json",
                }

                url = f"{API_ALERT_ENDPOINT}/{location_id}"
                _LOGGER.info("Fetching alerts for location ID: %s", location_id)

                async with async_timeout.timeout(10):
                    session = coordinator._smn_data._session
                    response = await session.get(url, headers=headers)
                    response.raise_for_status()
                    data = await response.json()

                # Parse and return alerts
                result = _parse_alerts(data)
                _LOGGER.info(
                    "Fetched alerts for location %s: %d active alerts with max severity '%s'",
                    location_id,
                    len(result.get("active_alerts", [])),
                    result.get("max_severity", "info")
                )
                return result

            except Exception as err:
                _LOGGER.error("Error fetching alerts for location %s: %s", location_id, err)
                return {"active_alerts": [], "max_severity": "info", "area_id": None, "error": str(err)}

        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ALERTS_FOR_LOCATION,
            handle_get_alerts_for_location,
            schema=SERVICE_GET_ALERTS_FOR_LOCATION_SCHEMA,
            supports_response="only",
        )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
