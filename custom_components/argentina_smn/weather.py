"""Weather platform for Argentina SMN."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_SUNNY,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sun import is_up
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_MAP,
    CONDITIONS_MAP,
    CONF_TRACK_HOME,
    DOMAIN,
    FORECAST_MAP,
    HOME_LOCATION_NAME,
)
from .coordinator import ArgentinaSMNDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def format_condition(condition: str, sun_is_up: bool = True) -> str:
    """Map SMN weather condition to HA condition."""
    if not condition:
        return ATTR_CONDITION_SUNNY if sun_is_up else ATTR_CONDITION_CLEAR_NIGHT

    condition_lower = condition.lower()

    # Check each HA condition mapping
    for ha_condition, smn_conditions in CONDITIONS_MAP.items():
        for smn_condition in smn_conditions:
            if smn_condition.lower() in condition_lower:
                # Special handling for clear/sunny vs clear night
                if ha_condition == ATTR_CONDITION_SUNNY and not sun_is_up:
                    return ATTR_CONDITION_CLEAR_NIGHT
                return ha_condition

    # Default to sunny/clear-night
    return ATTR_CONDITION_SUNNY if sun_is_up else ATTR_CONDITION_CLEAR_NIGHT


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Argentina SMN weather entity."""
    coordinator: ArgentinaSMNDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # Determine entity name
    if config_entry.data.get(CONF_TRACK_HOME, False):
        name = HOME_LOCATION_NAME
    else:
        name = config_entry.data.get("name", "Argentina SMN Weather")

    async_add_entities([ArgentinaSMNWeather(coordinator, name, config_entry)], False)


class ArgentinaSMNWeather(
    CoordinatorEntity[ArgentinaSMNDataUpdateCoordinator], WeatherEntity
):
    """Implementation of an Argentina SMN weather entity."""

    _attr_has_entity_name = True
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        coordinator: ArgentinaSMNDataUpdateCoordinator,
        name: str,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config_entry.entry_id)},
            manufacturer="Servicio Meteorológico Nacional",
            name=name,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data.current_weather_data:
            return None

        condition = self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("description", "description")
        )

        # Check if sun is up for proper day/night condition
        sun_up = is_up(self.hass)
        return format_condition(condition, sun_up)

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("temperature", "temp")
        )

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("humidity", "humidity")
        )

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("pressure", "pressure")
        )

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("wind_speed", "wind_speed")
        )

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("wind_bearing", "wind_bearing")
        )

    @property
    def native_visibility(self) -> float | None:
        """Return the visibility."""
        return self.coordinator.data.current_weather_data.get(
            ATTR_MAP.get("visibility", "visibility")
        )

    def _format_forecast(
        self, forecast_data: list[dict[str, Any]]
    ) -> list[Forecast]:
        """Format forecast data for Home Assistant."""
        if not forecast_data:
            return []

        forecasts: list[Forecast] = []

        for item in forecast_data:
            # Skip if missing required fields
            if not item.get("temperature") and not item.get("date"):
                continue

            forecast = Forecast(
                datetime=self._parse_datetime(
                    item.get("date") or item.get("datetime")
                ),
                native_temperature=item.get("temperature"),
                native_templow=item.get("templow") or item.get("temp_min"),
                condition=format_condition(
                    item.get("description") or item.get("weather", "")
                ),
                native_precipitation=item.get("precipitation") or item.get("rain"),
                native_wind_speed=item.get("wind_speed"),
                wind_bearing=item.get("wind_bearing") or item.get("wind_direction"),
                humidity=item.get("humidity"),
            )

            forecasts.append(forecast)

        return forecasts

    def _parse_datetime(self, date_str: str | None) -> str | None:
        """Parse datetime string to ISO format."""
        if not date_str:
            return None

        try:
            # Try parsing as ISO format
            dt = dt_util.parse_datetime(date_str)
            if dt:
                return dt.isoformat()

            # Try parsing as date only
            date_obj = dt_util.parse_date(date_str)
            if date_obj:
                return datetime.combine(
                    date_obj, datetime.min.time()
                ).isoformat()

            return date_str
        except (ValueError, TypeError):
            return date_str

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        return self._format_forecast(self.coordinator.data.daily_forecast)

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        return self._format_forecast(self.coordinator.data.hourly_forecast)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}

        # Add alerts if available
        if self.coordinator.data.alerts:
            attrs["alerts"] = self.coordinator.data.alerts

        # Add heat warnings if available
        if self.coordinator.data.heat_warnings:
            attrs["heat_warnings"] = self.coordinator.data.heat_warnings

        return attrs
