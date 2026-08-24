"""Test the resolver module"""

import pytest

from geoenv.resolver import Resolver
from geoenv.geometry import Geometry
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.data_sources import EcologicalMarineUnits
from geoenv.data_sources import GlobalLakesAndWetlands


@pytest.mark.asyncio
async def test_resolve(use_mock, scenarios, assert_identify, mocker):
    """Test the resolve method"""
    for scenario in scenarios:
        data_source_obj = scenario.get("data_source")
        if use_mock:
            mocker.patch.object(
                data_source_obj,
                "_request",
                mocker.AsyncMock(return_value=scenario.get("response").json()),
            )

        # Configure
        data_source = [data_source_obj]
        resolver = Resolver(data_source)
        geometry = Geometry(scenario.get("geometry"))

        # Run
        result = await resolver.resolve(geometry)

        # Assert
        assert_identify(result, scenario)


def test_data_source():
    """Test the data_source property"""
    # Get
    resolver = Resolver([WorldTerrestrialEcosystems()])
    assert resolver.data_source is not None
    assert isinstance(resolver.data_source, list)
    assert isinstance(resolver.data_source[0], WorldTerrestrialEcosystems)

    # Set
    resolver.data_source = [EcologicalMarineUnits(), GlobalLakesAndWetlands()]
    assert resolver.data_source is not None
    assert isinstance(resolver.data_source, list)
    assert isinstance(resolver.data_source[0], EcologicalMarineUnits)
    assert isinstance(resolver.data_source[1], GlobalLakesAndWetlands)
