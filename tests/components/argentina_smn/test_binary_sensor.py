"""Test the SMN binary sensor entities."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, STATE_ON, STATE_OFF
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
async def test_alert_sensor_on(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
    mock_alerts_data,
) -> None:
    """Test alert sensor is ON when alerts are active."""
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
        mock_data_instance.alerts = mock_alerts_data
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Get main alert sensor
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_weather_alert")
        assert state is not None
        assert state.state == STATE_ON
        assert state.attributes["active_alert_count"] == 2
        assert "tormenta" in state.attributes["alert_summary"]
        assert "lluvia" in state.attributes["alert_summary"]


@pytest.mark.asyncio
async def test_alert_sensor_off(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
) -> None:
    """Test alert sensor is OFF when no alerts are active."""
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

        # Get main alert sensor
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_weather_alert")
        assert state is not None
        assert state.state == STATE_OFF


@pytest.mark.asyncio
async def test_event_alert_sensors(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
    mock_alerts_data,
) -> None:
    """Test individual event alert sensors."""
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
        mock_data_instance.alerts = mock_alerts_data
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Test tormenta sensor is ON (event ID 41, level 3 in mock data)
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_alert_tormenta")
        assert state is not None
        assert state.state == STATE_ON
        assert state.attributes["level"] == 3
        assert state.attributes["severity"] == "warning"

        # Test lluvia sensor is ON (event ID 37, level 2 in mock data)
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_alert_lluvia")
        assert state is not None
        assert state.state == STATE_ON
        assert state.attributes["level"] == 2

        # Test nevada sensor is OFF (not in mock data)
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_alert_nevada")
        assert state is not None
        assert state.state == STATE_OFF


@pytest.mark.asyncio
async def test_shortterm_alert_sensor(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
    mock_shortterm_alerts,
) -> None:
    """Test short-term alert sensor."""
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
        mock_data_instance.shortterm_alerts = mock_shortterm_alerts
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Get short-term alert sensor
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_short_term_alert")
        assert state is not None
        assert state.state == STATE_ON
        assert state.attributes["alert_count"] == 1
        assert "TORMENTAS FUERTES" in state.attributes["title"]
        assert "BUENOS AIRES: Ayacucho" in str(state.attributes["zones"])


@pytest.mark.asyncio
async def test_alert_sensor_icons(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_current_weather,
    mock_alerts_data,
) -> None:
    """Test alert sensors have correct MDI icons."""
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
        mock_data_instance.alerts = mock_alerts_data
        mock_data_instance.shortterm_alerts = []
        mock_data_instance.heat_warnings = {}
        mock_data_instance.fetch_data = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Test main alert sensor icon
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_weather_alert")
        assert state is not None
        assert state.attributes["icon"] == "mdi:alert"

        # Test tormenta sensor icon
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_alert_tormenta")
        assert state is not None
        assert state.attributes["icon"] == "mdi:weather-lightning"

        # Test lluvia sensor icon
        state = hass.states.get("binary_sensor.ciudad_de_buenos_aires_alert_lluvia")
        assert state is not None
        assert state.attributes["icon"] == "mdi:weather-rainy"
