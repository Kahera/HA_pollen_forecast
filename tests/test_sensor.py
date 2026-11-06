from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.pollenvarsel_naaf_yr.const import (
    CONF_LOCATION_ID,
    CONF_LOCATION_NAME,
    CONF_LOCATIONS,
    CONF_POLLEN_TYPES,
    DOMAIN,
)
from custom_components.pollenvarsel_naaf_yr.coordinator import PollenDataCoordinator
from custom_components.pollenvarsel_naaf_yr.sensor import async_setup_entry


async def test_sensor_setup_uses_entry_title_for_empty_region_name(hass):
    location_id = "1-123"
    coordinator = PollenDataCoordinator(hass, language="en")
    coordinator.location_data[location_id] = {
        "region_name": "",
        "data": {
            "today": {
                "birch": {
                    "level": "moderate",
                    "level_name": "Moderate",
                    "pollen_name": "Birch",
                    "date": "2026-06-01",
                }
            }
        },
        "dates": {"tomorrow": "2026-06-02"},
        "last_updated": "2026-06-01T08:00:00+00:00",
    }
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Fallback Region",
        data={
            CONF_LOCATIONS: [
                {
                    CONF_LOCATION_ID: location_id,
                    CONF_LOCATION_NAME: "",
                }
            ],
            CONF_POLLEN_TYPES: ["birch"],
        },
    )
    entry.runtime_data = coordinator
    entities = []

    await async_setup_entry(hass, entry, entities.extend)

    assert len(entities) == 2
    today, tomorrow = entities
    assert today._display_name == "Fallback Region"
    assert today.entity_id.startswith("sensor.pollen_birch_")
    assert "__" not in today.entity_id
    assert today.device_info["name"] == "Fallback Region"
    assert today.state == "moderate"
    assert today.extra_state_attributes == {
        "date": "2026-06-01",
        "pollen_name": "Birch",
        "region_name": "",
        "last_updated": "2026-06-01T08:00:00+00:00",
        "level_name": "Moderate",
        "level_color": "orange",
    }
    assert tomorrow.state == "none"
    assert tomorrow.extra_state_attributes["date"] == "2026-06-02"