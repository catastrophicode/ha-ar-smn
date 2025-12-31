"""Test the SMN config flow."""
from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.argentina_smn.const import DOMAIN


@pytest.mark.asyncio
async def test_form_home_location(
    hass: HomeAssistant, mock_token_manager, mock_location_data
) -> None:
    """Test we can configure with home location coordinates."""
    # Set home location
    hass.config.latitude = -34.6217
    hass.config.longitude = -58.4258

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.argentina_smn.config_flow.ArgentinaSMNDataUpdateCoordinator"
    ) as mock_coordinator, patch(
        "custom_components.argentina_smn.async_setup_entry", return_value=True
    ):
        mock_coordinator_instance = mock_coordinator.return_value
        mock_coordinator_instance._smn_data._token_manager = mock_token_manager
        mock_coordinator_instance._smn_data.fetch_location_by_coords = AsyncMock(
            return_value=mock_location_data
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_LATITUDE: -34.6217,
                CONF_LONGITUDE: -58.4258,
                CONF_NAME: "My Home",
            },
        )

        await hass.async_block_till_done()

        assert result2["type"] == FlowResultType.CREATE_ENTRY
        assert result2["title"] == "My Home"
        assert result2["data"] == {
            CONF_LATITUDE: -34.6217,
            CONF_LONGITUDE: -58.4258,
            CONF_NAME: "My Home",
        }


@pytest.mark.asyncio
async def test_form_custom_location(
    hass: HomeAssistant, mock_token_manager, mock_location_data
) -> None:
    """Test we can configure with custom location."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.argentina_smn.config_flow.ArgentinaSMNDataUpdateCoordinator"
    ) as mock_coordinator, patch(
        "custom_components.argentina_smn.async_setup_entry", return_value=True
    ):
        mock_coordinator_instance = mock_coordinator.return_value
        mock_coordinator_instance._smn_data._token_manager = mock_token_manager
        mock_coordinator_instance._smn_data.fetch_location_by_coords = AsyncMock(
            return_value=mock_location_data
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_LATITUDE: -31.4201,
                CONF_LONGITUDE: -64.1888,
                CONF_NAME: "Córdoba",
            },
        )

        await hass.async_block_till_done()

        assert result2["type"] == FlowResultType.CREATE_ENTRY
        assert result2["title"] == "Córdoba"
        assert result2["data"] == {
            CONF_LATITUDE: -31.4201,
            CONF_LONGITUDE: -64.1888,
            CONF_NAME: "Córdoba",
        }


@pytest.mark.asyncio
async def test_form_already_configured(
    hass: HomeAssistant, mock_token_manager, mock_location_data
) -> None:
    """Test we handle already configured."""
    # Create an existing entry
    existing_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=1,
        domain=DOMAIN,
        title="Buenos Aires",
        data={
            CONF_LATITUDE: -34.6217,
            CONF_LONGITUDE: -58.4258,
            CONF_NAME: "Buenos Aires",
        },
        source=config_entries.SOURCE_USER,
        options={},
        unique_id="buenos_aires",
    )
    existing_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    with patch(
        "custom_components.argentina_smn.config_flow.ArgentinaSMNDataUpdateCoordinator"
    ) as mock_coordinator:
        mock_coordinator_instance = mock_coordinator.return_value
        mock_coordinator_instance._smn_data._token_manager = mock_token_manager
        mock_coordinator_instance._smn_data.fetch_location_by_coords = AsyncMock(
            return_value=mock_location_data
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_LATITUDE: -34.6217,
                CONF_LONGITUDE: -58.4258,
                CONF_NAME: "Another Name",
            },
        )

        await hass.async_block_till_done()

        assert result2["type"] == FlowResultType.ABORT
        assert result2["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_form_api_error(hass: HomeAssistant, mock_token_manager) -> None:
    """Test we handle API errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM

    with patch(
        "custom_components.argentina_smn.config_flow.ArgentinaSMNDataUpdateCoordinator"
    ) as mock_coordinator:
        mock_coordinator_instance = mock_coordinator.return_value
        mock_coordinator_instance._smn_data._token_manager = mock_token_manager
        mock_coordinator_instance._smn_data.fetch_location_by_coords = AsyncMock(
            side_effect=Exception("API Error")
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_LATITUDE: -31.4201,
                CONF_LONGITUDE: -64.1888,
                CONF_NAME: "Test Location",
            },
        )

        await hass.async_block_till_done()

        assert result2["type"] == FlowResultType.FORM
        assert result2["errors"] == {"base": "cannot_connect"}
