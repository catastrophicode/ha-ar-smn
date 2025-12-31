"""Test the SMN integration initialization."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from custom_components.argentina_smn.const import DOMAIN


@pytest.fixture
def mock_config_entry() -> ConfigEntry:
    """Return a mock config entry."""
    return ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="José María Ezeiza",
        data={
            CONF_LATITUDE: -34.8604,
            CONF_LONGITUDE: -58.522,
            "name": "José María Ezeiza",
        },
        source="user",
        unique_id="4841",
    )


@pytest.mark.asyncio
async def test_setup_entry(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_coordinator_data,
) -> None:
    """Test successful setup of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData.fetch_data",
        new_callable=AsyncMock,
    ) as mock_fetch:
        mock_token_class.return_value = mock_token_manager
        mock_fetch.return_value = None

        with patch(
            "custom_components.argentina_smn.async_setup_entry", return_value=True
        ):
            assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
) -> None:
    """Test successful unload of entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData.fetch_data",
        new_callable=AsyncMock,
    ):
        mock_token_class.return_value = mock_token_manager

        with patch(
            "custom_components.argentina_smn.async_setup_entry", return_value=True
        ), patch(
            "custom_components.argentina_smn.async_unload_entry", return_value=True
        ):
            assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
            await hass.async_block_till_done()


@pytest.mark.asyncio
async def test_service_get_alerts(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_alerts_data,
) -> None:
    """Test get_alerts service call."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData"
    ) as mock_data_class:
        mock_token_class.return_value = mock_token_manager
        mock_data_instance = mock_data_class.return_value
        mock_data_instance.alerts = mock_alerts_data
        mock_data_instance.fetch_data = AsyncMock()

        # Import after patches are set up
        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Call the service
        response = await hass.services.async_call(
            DOMAIN,
            "get_alerts",
            {"config_entry_id": mock_config_entry.entry_id},
            blocking=True,
            return_response=True,
        )

        assert response is not None
        assert "active_alerts" in response


@pytest.mark.asyncio
async def test_service_get_alerts_for_location(
    hass: HomeAssistant,
    mock_config_entry: ConfigEntry,
    mock_token_manager,
    mock_alerts_data,
) -> None:
    """Test get_alerts_for_location service call."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.argentina_smn.coordinator.SMNTokenManager"
    ) as mock_token_class, patch(
        "custom_components.argentina_smn.coordinator.ArgentinaSMNData"
    ) as mock_data_class, patch(
        "aiohttp.ClientSession.get"
    ) as mock_get:
        mock_token_class.return_value = mock_token_manager
        mock_data_instance = mock_data_class.return_value
        mock_data_instance._session = AsyncMock()
        mock_data_instance._token_manager = mock_token_manager
        mock_data_instance.fetch_data = AsyncMock()

        # Mock API response
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_alerts_data)
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aexit__ = AsyncMock()

        from custom_components.argentina_smn import async_setup_entry

        assert await async_setup_entry(hass, mock_config_entry)
        await hass.async_block_till_done()

        # Call the service
        response = await hass.services.async_call(
            DOMAIN,
            "get_alerts_for_location",
            {"location_id": "4864"},
            blocking=True,
            return_response=True,
        )

        assert response is not None
        assert "active_alerts" in response
