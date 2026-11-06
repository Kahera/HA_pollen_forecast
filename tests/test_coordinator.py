from unittest.mock import Mock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pollenvarsel_naaf_yr.const import (
    CONF_LOCATION_ID,
    CONF_LOCATIONS,
    DOMAIN,
)
from custom_components.pollenvarsel_naaf_yr.coordinator import PollenDataCoordinator


class MockResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self.payload = payload or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def json(self):
        return self.payload


@pytest.mark.parametrize("language", ["nb", "en"])
async def test_update_data_parses_today_and_tomorrow(hass, language):
    location_id = "1-123"
    payload = {
        "_embedded": {
            "regionName": "Oslo",
            "pollenForecast": [
                {
                    "date": "2026-06-01",
                    "distributions": {
                        "moderate": {
                            "distributionName": "Moderate",
                            "pollenTypes": [{"id": "birch", "name": "Birch"}],
                        }
                    },
                },
                {
                    "date": "2026-06-02",
                    "distributions": {
                        "severe": {
                            "distributionName": "Severe",
                            "pollenTypes": [{"id": "grass", "name": "Grass"}],
                        }
                    },
                },
            ],
        }
    }
    response = MockResponse(200, payload)
    session = Mock()
    session.get.return_value = response
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LOCATIONS: [{CONF_LOCATION_ID: location_id}]},
    )
    coordinator = PollenDataCoordinator(hass, language=language)
    coordinator.config_entry = entry

    with patch(
        "custom_components.pollenvarsel_naaf_yr.coordinator.async_get_clientsession",
        return_value=session,
    ):
        result = await coordinator._async_update_data()

    assert session.get.call_args.args[0].endswith(
        f"/{location_id}/pollen?language={language}"
    )
    assert result["locations"][location_id]["region_name"] == "Oslo"
    assert result["locations"][location_id]["data"]["today"]["birch"] == {
        "level": "moderate",
        "level_name": "Moderate",
        "pollen_name": "Birch",
        "date": "2026-06-01",
    }
    assert result["locations"][location_id]["data"]["tomorrow"]["grass"][
        "level"
    ] == "severe"


async def test_update_data_keeps_successful_locations_when_another_fails(hass):
    failed_location = "1-failed"
    successful_location = "1-success"
    session = Mock()
    session.get.side_effect = [
        MockResponse(503),
        MockResponse(200, {"_embedded": {"regionName": "Oslo"}}),
    ]
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_LOCATIONS: [
                {CONF_LOCATION_ID: failed_location},
                {CONF_LOCATION_ID: successful_location},
            ]
        },
    )
    coordinator = PollenDataCoordinator(hass)
    coordinator.config_entry = entry

    with patch(
        "custom_components.pollenvarsel_naaf_yr.coordinator.async_get_clientsession",
        return_value=session,
    ):
        result = await coordinator._async_update_data()

    assert failed_location not in result["locations"]
    assert result["locations"][successful_location]["region_name"] == "Oslo"