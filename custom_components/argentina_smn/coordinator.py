"""DataUpdateCoordinator for the Argentina SMN integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ALERT_ENDPOINT,
    API_COORD_ENDPOINT,
    API_FORECAST_ENDPOINT,
    API_HEAT_WARNING_ENDPOINT,
    CONF_TRACK_HOME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ArgentinaSMNData:
    """Class to handle Argentina SMN data."""

    def __init__(
        self,
        hass: HomeAssistant,
        latitude: float,
        longitude: float,
        location_id: str | None = None,
    ) -> None:
        """Initialize the data object."""
        self._hass = hass
        self._latitude = latitude
        self._longitude = longitude
        self._location_id = location_id
        self._session = async_get_clientsession(hass)

        self.current_weather_data: dict[str, Any] = {}
        self.daily_forecast: list[dict[str, Any]] = []
        self.hourly_forecast: list[dict[str, Any]] = []
        self.alerts: list[dict[str, Any]] = []
        self.heat_warnings: list[dict[str, Any]] = []

    async def _get_location_id(self) -> str:
        """Get the location ID from coordinates."""
        if self._location_id:
            return self._location_id

        url = f"{API_COORD_ENDPOINT}?lat={self._latitude}&lon={self._longitude}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()
                data = await response.json()

                # Extract location ID from response
                # The actual key might differ - adjust based on API response
                if isinstance(data, dict):
                    self._location_id = str(data.get("id") or data.get("location_id"))
                elif isinstance(data, list) and len(data) > 0:
                    self._location_id = str(data[0].get("id") or data[0].get("location_id"))
                else:
                    raise UpdateFailed(f"Unexpected response format: {data}")

                _LOGGER.debug("Location ID for %s,%s: %s", self._latitude, self._longitude, self._location_id)
                return self._location_id

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching location ID: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching location ID: {err}") from err

    async def fetch_data(self) -> None:
        """Fetch data from SMN API."""
        try:
            # Get location ID if not already set
            location_id = await self._get_location_id()

            # Fetch forecast data
            await self._fetch_forecast(location_id)

            # Fetch alerts
            await self._fetch_alerts(location_id)

        except Exception as err:
            raise UpdateFailed(f"Error fetching SMN data: {err}") from err

    async def _fetch_forecast(self, location_id: str) -> None:
        """Fetch forecast data."""
        url = f"{API_FORECAST_ENDPOINT}/{location_id}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()
                data = await response.json()

                # Parse current weather from forecast data
                # The structure will depend on the actual API response
                if isinstance(data, list) and len(data) > 0:
                    current = data[0]
                    self.current_weather_data = {
                        "temp": current.get("temperature"),
                        "humidity": current.get("humidity"),
                        "pressure": current.get("pressure"),
                        "wind_speed": current.get("wind_speed"),
                        "wind_bearing": current.get("wind_direction"),
                        "description": current.get("description") or current.get("weather"),
                    }

                    # Store forecast data
                    self.daily_forecast = data
                    self.hourly_forecast = data
                elif isinstance(data, dict):
                    # Handle if response is a dict with current/forecast keys
                    self.current_weather_data = data.get("current", {})
                    self.daily_forecast = data.get("forecast", [])
                    self.hourly_forecast = data.get("hourly", [])

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching forecast: %s", err)
        except Exception as err:
            _LOGGER.error("Unexpected error fetching forecast: %s", err)

    async def _fetch_alerts(self, location_id: str) -> None:
        """Fetch weather alerts."""
        url = f"{API_ALERT_ENDPOINT}/{location_id}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()
                data = await response.json()

                # Store alerts
                if isinstance(data, list):
                    self.alerts = data
                elif isinstance(data, dict):
                    self.alerts = [data]

                    # Get area_id for heat warnings if available
                    area_id = data.get("area_id")
                    if area_id:
                        await self._fetch_heat_warnings(area_id)

        except aiohttp.ClientError as err:
            _LOGGER.debug("Error fetching alerts (may be normal if none): %s", err)
        except Exception as err:
            _LOGGER.debug("Unexpected error fetching alerts: %s", err)

    async def _fetch_heat_warnings(self, area_id: str) -> None:
        """Fetch heat warnings."""
        url = f"{API_HEAT_WARNING_ENDPOINT}/{area_id}"

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url)
                response.raise_for_status()
                data = await response.json()

                if isinstance(data, list):
                    self.heat_warnings = data
                elif isinstance(data, dict):
                    self.heat_warnings = [data]

        except aiohttp.ClientError as err:
            _LOGGER.debug("Error fetching heat warnings (may be normal if none): %s", err)
        except Exception as err:
            _LOGGER.debug("Unexpected error fetching heat warnings: %s", err)


class ArgentinaSMNDataUpdateCoordinator(DataUpdateCoordinator[ArgentinaSMNData]):
    """Class to manage fetching Argentina SMN data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.track_home = config_entry.data.get(CONF_TRACK_HOME, False)

        if self.track_home:
            latitude = hass.config.latitude
            longitude = hass.config.longitude
        else:
            latitude = config_entry.data[CONF_LATITUDE]
            longitude = config_entry.data[CONF_LONGITUDE]

        self.data = ArgentinaSMNData(hass, latitude, longitude)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> ArgentinaSMNData:
        """Fetch data from API."""
        await self.data.fetch_data()
        return self.data

    def track_home_location(self) -> None:
        """Track changes in home location."""

        async def handle_home_location_update(event: Event) -> None:
            """Handle home location update."""
            self.data._latitude = self.hass.config.latitude
            self.data._longitude = self.hass.config.longitude
            self.data._location_id = None  # Reset to force refetch
            await self.async_request_refresh()

        # This would need to be implemented with proper event tracking
        # For now, we'll keep it simple
