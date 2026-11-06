from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.data_entry_flow import FlowResultType

from custom_components.pollenvarsel_naaf_yr.config_flow import PollenvarselConfigFlow
from custom_components.pollenvarsel_naaf_yr.const import (
    CONF_LANGUAGE,
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    CONF_LOCATIONS,
    CONF_POLLEN_TYPES,
    CONF_UPDATE_FREQUENCY,
    DEFAULT_LANGUAGE,
    DEFAULT_UPDATE_FREQUENCY,
    DOMAIN,
)


async def test_config_flow_requires_location_id(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_LOCATION_ID: " "},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "location_required"}


async def test_config_flow_normalizes_location_and_falls_back_to_id(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
    )
    user_input = {
        CONF_LOCATION_ID: " 1-189277 ",
        CONF_LOCATION_NAME: "",
        CONF_POLLEN_TYPES: ["birch"],
        CONF_UPDATE_FREQUENCY: DEFAULT_UPDATE_FREQUENCY,
        CONF_LANGUAGE: DEFAULT_LANGUAGE,
    }

    with patch.object(
        PollenvarselConfigFlow,
        "_async_fetch_region_name",
        new=AsyncMock(return_value=""),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=user_input,
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "1-189277"
    assert result["data"][CONF_LOCATIONS] == [
        {CONF_LOCATION_ID: "1-189277", CONF_LOCATION_NAME: ""}
    ]