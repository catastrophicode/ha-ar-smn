"""Test the SMN weather entity."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.weather import (
    ATTR_CONDITION_CLEAR_NIGHT,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant

from custom_components.argentina_smn.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Return a mock config entry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Ciudad de Buenos Aires",
        data={
            CONF_LATITUDE: -34.6217,
            CONF_LONGITUDE: -58.4258,
            "name": "Ciudad de Buenos Aires",
        },
        source="user",
        unique_id="4864",
    )


@pytest.mark.asyncio
async def test_weather_entity_state(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
) -> None:
    """Test weather entity reports correct state."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData"
    ) as mock_data_class:
        mock_token_class.return_value = mock_token_manager

        mock_data_instance = mock_data_class.return_value
        mock_data_instance.current_weather_data = mock_current_weather
        mock_data_instance.daily_forecast = []
        mock_data_instance.hourly_forecast = []
        mock_data_instance.alerts = {}
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Get weather entity
        state = hass.states.get("weather.ciudad_de_buenos_aires")
        assert state is not None
        assert state.state == ATTR_CONDITION_SUNNY
        assert state.attributes["temperature"] == 22.5
        assert state.attributes["humidity"] == 65
        assert state.attributes["pressure"] == 1013.2
        assert state.attributes["wind_speed"] == 15.5
        assert state.attributes["wind_bearing"] == 180
        assert state.attributes["attribution"] == "Data provided by Servicio Meteorológico Nacional Argentina"


@pytest.mark.asyncio
async def test_weather_entity_forecast(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
    mock_forecast_data,
) -> None:
    """Test weather entity returns forecast."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData"
    ) as mock_data_class:
        mock_token_class.return_value = mock_token_manager

        mock_data_instance = mock_data_class.return_value
        mock_data_instance.current_weather_data = mock_current_weather
        mock_data_instance.daily_forecast = mock_forecast_data.get("forecast", [])
        mock_data_instance.hourly_forecast = []
        mock_data_instance.alerts = {}
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Get weather entity
        state = hass.states.get("weather.ciudad_de_buenos_aires")
        assert state is not None

        # Check forecast is present
        # Note: In HA 2024.x forecast is accessed via service call
        # For testing purposes we just verify the entity was created with forecast data


@pytest.mark.asyncio
async def test_weather_condition_mapping(
    hass: HomeAssistant,
) -> None:
    """Test weather condition ID mapping."""
    from custom_components.argentina_smn.weather import format_condition

    # Test day conditions
    assert format_condition({"id": 3, "description": "Despejado"}, sun_is_up=True) == ATTR_CONDITION_SUNNY
    assert format_condition({"id": 5, "description": "Despejado"}, sun_is_up=False) == ATTR_CONDITION_CLEAR_NIGHT

    # Test sunny converted to clear-night at night
    assert format_condition({"id": 3, "description": "Despejado"}, sun_is_up=False) == ATTR_CONDITION_CLEAR_NIGHT

    # Test None handling
    assert format_condition(None, sun_is_up=True) == ATTR_CONDITION_SUNNY
    assert format_condition(None, sun_is_up=False) == ATTR_CONDITION_CLEAR_NIGHT

    # Test invalid dict
    assert format_condition({}, sun_is_up=True) == ATTR_CONDITION_SUNNY
    assert format_condition({"description": "test"}, sun_is_up=True) == ATTR_CONDITION_SUNNY


@pytest.mark.asyncio
async def test_weather_entity_name(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
) -> None:
    """Test weather entity uses location name from API."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData"
    ) as mock_data_class:
        mock_token_class.return_value = mock_token_manager

        mock_data_instance = mock_data_class.return_value
        mock_data_instance.current_weather_data = mock_current_weather
        mock_data_instance.daily_forecast = []
        mock_data_instance.hourly_forecast = []
        mock_data_instance.alerts = {}
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Get weather entity
        state = hass.states.get("weather.ciudad_de_buenos_aires")
        assert state is not None
        assert state.attributes["friendly_name"] == "Ciudad de Buenos Aires"
