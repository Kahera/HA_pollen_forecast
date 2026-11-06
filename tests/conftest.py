import pytest


@pytest.fixture(autouse=True)
def enable_custom_integrations_fixture(enable_custom_integrations):
    """Allow tests to load this custom integration."""
    yield