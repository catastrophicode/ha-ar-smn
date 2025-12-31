"""Config flow for SMN Weather integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv

from .const import (
    DEFAULT_HOME_LATITUDE,
    DEFAULT_HOME_LONGITUDE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_validate_location(
    hass: HomeAssistant, latitude: float, longitude: float
) -> dict[str, str] | None:
    """Validate the location coordinates."""
    # Basic validation - could be extended to check if location is in Argentina
    if not (-90 <= latitude <= 90):
        return {"base": "invalid_latitude"}
    if not (-180 <= longitude <= 180):
        return {"base": "invalid_longitude"}

    # Optional: Check if coordinates are roughly in Argentina
    # Argentina bounds approximately: lat -55 to -22, lon -73 to -53
    if not (-55 <= latitude <= -22):
        _LOGGER.warning(
            "Latitude %s is outside Argentina bounds (-55 to -22)", latitude
        )
    if not (-73 <= longitude <= -53):
        _LOGGER.warning(
            "Longitude %s is outside Argentina bounds (-73 to -53)", longitude
        )

    return None


class ArgentinaSMNConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMN Weather."""

    VERSION = 1

    @callback
    def _async_check_unique_id(
        self, latitude: float, longitude: float
    ) -> tuple[bool, str | None]:
        """Check if the location is already configured.

        Returns:
            Tuple of (is_unique, existing_entry_title)
        """
        # Tolerance for coordinate comparison (0.0001 degrees ≈ 11 meters)
        COORD_TOLERANCE = 0.0001

        # Check existing entries
        existing_entries = self._async_current_entries()
        _LOGGER.debug(
            "Checking uniqueness for lat=%s, lon=%s. Found %d existing entries",
            latitude,
            longitude,
            len(existing_entries),
        )

        for entry in existing_entries:
            entry_lat = entry.data.get(CONF_LATITUDE)
            entry_lon = entry.data.get(CONF_LONGITUDE)

            _LOGGER.debug(
                "Checking entry: %s (lat=%s, lon=%s)",
                entry.title,
                entry_lat,
                entry_lon,
            )

            # Check against configured coordinates with tolerance
            if entry_lat is not None and entry_lon is not None:
                if (
                    abs(entry_lat - latitude) < COORD_TOLERANCE
                    and abs(entry_lon - longitude) < COORD_TOLERANCE
                ):
                    _LOGGER.warning(
                        "Location matches existing entry: %s (lat=%s, lon=%s)",
                        entry.title,
                        entry_lat,
                        entry_lon,
                    )
                    return (False, entry.title)

        _LOGGER.debug("Location is unique, allowing setup")
        return (True, None)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            name = user_input.get(CONF_NAME, f"SMN {latitude}, {longitude}")

            # Validate coordinates
            validation_errors = await async_validate_location(
                self.hass, latitude, longitude
            )
            if validation_errors:
                errors.update(validation_errors)
            else:
                # Check if already configured
                is_unique, existing_title = self._async_check_unique_id(latitude, longitude)
                if not is_unique:
                    errors["base"] = "already_configured"
                    _LOGGER.warning(
                        "Location %s, %s is already configured as '%s'",
                        latitude,
                        longitude,
                        existing_title,
                    )
                else:
                    # Create entry
                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_NAME: name,
                            CONF_LATITUDE: latitude,
                            CONF_LONGITUDE: longitude,
                        },
                    )

        # Show form - pre-fill with home coordinates
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE, default=self.hass.config.longitude
                ): cv.longitude,
                vol.Optional(CONF_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_onboarding(
        self, data: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle onboarding step."""
        # Don't create an entry if latitude or longitude isn't set.
        # Also, filters out our onboarding default location.
        if (
            not self.hass.config.latitude
            or not self.hass.config.longitude
            or (
                self.hass.config.latitude == DEFAULT_HOME_LATITUDE
                and self.hass.config.longitude == DEFAULT_HOME_LONGITUDE
            )
        ):
            return self.async_abort(reason="no_home")

        return await self.async_step_user()
