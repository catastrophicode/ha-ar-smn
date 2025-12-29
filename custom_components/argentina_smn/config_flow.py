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
    CONF_TRACK_HOME,
    DEFAULT_HOME_LATITUDE,
    DEFAULT_HOME_LONGITUDE,
    DOMAIN,
    HOME_LOCATION_NAME,
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
    ) -> bool:
        """Check if the location is already configured."""
        location_key = f"{latitude}-{longitude}"

        # Check existing entries
        for entry in self._async_current_entries():
            if entry.data.get(CONF_TRACK_HOME):
                # If tracking home, check against home location
                if (
                    self.hass.config.latitude == latitude
                    and self.hass.config.longitude == longitude
                ):
                    return False
            else:
                # Check against configured coordinates
                entry_lat = entry.data.get(CONF_LATITUDE)
                entry_lon = entry.data.get(CONF_LONGITUDE)
                if entry_lat == latitude and entry_lon == longitude:
                    return False

        return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if tracking home location
            if user_input.get(CONF_TRACK_HOME, False):
                latitude = self.hass.config.latitude
                longitude = self.hass.config.longitude
                name = HOME_LOCATION_NAME
            else:
                latitude = user_input[CONF_LATITUDE]
                longitude = user_input[CONF_LONGITUDE]
                name = user_input.get(CONF_NAME, f"SMN {latitude}, {longitude}")

            # Validate coordinates
            validation_errors = await async_validate_location(
                self.hass, latitude, longitude
            )
            if validation_errors:
                errors.update(validation_errors)
            # Check if already configured
            elif not self._async_check_unique_id(latitude, longitude):
                errors["base"] = "already_configured"
            else:
                # Create entry
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_LATITUDE: latitude,
                        CONF_LONGITUDE: longitude,
                        CONF_TRACK_HOME: user_input.get(CONF_TRACK_HOME, False),
                    },
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_TRACK_HOME, default=False): cv.boolean,
                vol.Optional(
                    CONF_LATITUDE, default=self.hass.config.latitude
                ): cv.latitude,
                vol.Optional(
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
