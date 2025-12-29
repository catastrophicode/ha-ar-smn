"""DataUpdateCoordinator for the SMN integration."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta
import json
import logging
import re
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    API_ALERT_ENDPOINT,
    API_COORD_ENDPOINT,
    API_FORECAST_ENDPOINT,
    API_HEAT_WARNING_ENDPOINT,
    CONF_TRACK_HOME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class SMNTokenManager:
    """Manage JWT token for SMN API authentication."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the token manager."""
        self._session = session
        self._token: str | None = None
        self._token_expiration: datetime | None = None

    def _decode_jwt_payload(self, token: str) -> dict[str, Any]:
        """Decode JWT payload without verification."""
        try:
            # Split the JWT into parts
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            # Decode the payload (second part)
            # Add padding if needed
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding

            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)
        except Exception as err:
            _LOGGER.error("Error decoding JWT: %s", err)
            return {}

    async def fetch_token(self) -> str:
        """Fetch JWT token from SMN website."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(TOKEN_URL)
                response.raise_for_status()
                html = await response.text()

                # Look for token in localStorage.setItem or similar patterns
                # Pattern: localStorage.setItem('token', 'eyJ...')
                token_pattern = r"localStorage\.setItem\(['\"]token['\"]\s*,\s*['\"]([^'\"]+)['\"]"
                match = re.search(token_pattern, html)

                if not match:
                    # Try alternative pattern: "token":"eyJ..."
                    token_pattern = r"['\"]token['\"]\s*:\s*['\"]([^'\"]+)['\"]"
                    match = re.search(token_pattern, html)

                if not match:
                    raise UpdateFailed("Could not find token in HTML")

                token = match.group(1)
                _LOGGER.debug("Successfully fetched JWT token")

                # Decode token to get expiration
                payload = self._decode_jwt_payload(token)
                if "exp" in payload:
                    self._token_expiration = datetime.fromtimestamp(
                        payload["exp"], tz=dt_util.UTC
                    )
                    _LOGGER.debug(
                        "Token expires at: %s", self._token_expiration.isoformat()
                    )

                self._token = token
                return token

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching token: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error fetching token: {err}") from err

    async def get_token(self) -> str:
        """Get valid token, refreshing if necessary."""
        # Check if we have a token and it's still valid
        if self._token and self._token_expiration:
            # Refresh if token expires in less than 5 minutes
            if dt_util.utcnow() < (self._token_expiration - timedelta(minutes=5)):
                return self._token

        # Fetch new token
        return await self.fetch_token()

    @property
    def token_expiration(self) -> datetime | None:
        """Return token expiration time."""
        return self._token_expiration


class ArgentinaSMNData:
    """Class to handle SMN data."""

    def __init__(
        self,
        hass: HomeAssistant,
        latitude: float,
        longitude: float,
        token_manager: SMNTokenManager,
        location_id: str | None = None,
    ) -> None:
        """Initialize the data object."""
        self._hass = hass
        self._latitude = latitude
        self._longitude = longitude
        self._location_id = location_id
        self._session = async_get_clientsession(hass)
        self._token_manager = token_manager

        self.current_weather_data: dict[str, Any] = {}
        self.daily_forecast: list[dict[str, Any]] = []
        self.hourly_forecast: list[dict[str, Any]] = []
        self.alerts: list[dict[str, Any]] = []
        self.heat_warnings: list[dict[str, Any]] = []

    async def _get_headers(self) -> dict[str, str]:
        """Get headers with authentication token."""
        token = await self._token_manager.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _get_location_id(self) -> str:
        """Get the location ID from coordinates."""
        if self._location_id:
            return self._location_id

        url = f"{API_COORD_ENDPOINT}?lat={self._latitude}&lon={self._longitude}"
        headers = await self._get_headers()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, headers=headers)
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
        headers = await self._get_headers()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, headers=headers)
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
        headers = await self._get_headers()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, headers=headers)
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
        headers = await self._get_headers()

        try:
            async with async_timeout.timeout(10):
                response = await self._session.get(url, headers=headers)
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
    """Class to manage fetching SMN data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.track_home = config_entry.data.get(CONF_TRACK_HOME, False)
        self._token_refresh_unsub = None

        if self.track_home:
            latitude = hass.config.latitude
            longitude = hass.config.longitude
        else:
            latitude = config_entry.data[CONF_LATITUDE]
            longitude = config_entry.data[CONF_LONGITUDE]

        # Create token manager
        session = async_get_clientsession(hass)
        self._token_manager = SMNTokenManager(session)

        # Store data handler before calling super().__init__
        self._smn_data = ArgentinaSMNData(hass, latitude, longitude, self._token_manager)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> ArgentinaSMNData:
        """Fetch data from API."""
        await self._smn_data.fetch_data()

        # Schedule token refresh if needed
        self._schedule_token_refresh()

        return self._smn_data

    def _schedule_token_refresh(self) -> None:
        """Schedule token refresh before expiration."""
        # Cancel existing refresh if any
        if self._token_refresh_unsub:
            self._token_refresh_unsub()
            self._token_refresh_unsub = None

        # Get token expiration
        expiration = self._token_manager.token_expiration
        if not expiration:
            return

        # Schedule refresh 5 minutes before expiration
        now = dt_util.utcnow()
        refresh_time = expiration - timedelta(minutes=5)

        if refresh_time <= now:
            # Token expires very soon, will be refreshed on next data fetch
            return

        # Calculate seconds until refresh
        seconds_until_refresh = (refresh_time - now).total_seconds()

        _LOGGER.debug(
            "Scheduling token refresh in %.0f seconds (at %s)",
            seconds_until_refresh,
            refresh_time.isoformat(),
        )

        async def _refresh_token(now):
            """Refresh token callback."""
            try:
                await self._token_manager.fetch_token()
                _LOGGER.info("Token refreshed successfully")
                # Schedule next refresh
                self._schedule_token_refresh()
            except Exception as err:
                _LOGGER.error("Failed to refresh token: %s", err)

        self._token_refresh_unsub = async_call_later(
            self.hass, seconds_until_refresh, _refresh_token
        )

    def track_home_location(self) -> None:
        """Track changes in home location."""

        async def handle_home_location_update(event: Event) -> None:
            """Handle home location update."""
            self._smn_data._latitude = self.hass.config.latitude
            self._smn_data._longitude = self.hass.config.longitude
            self._smn_data._location_id = None  # Reset to force refetch
            await self.async_request_refresh()

        # This would need to be implemented with proper event tracking
        # For now, we'll keep it simple
