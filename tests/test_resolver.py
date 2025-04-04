"""Test the resolver module"""

from geoenv.resolver import Resolver
from geoenv.geometry import Geometry
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.data_sources import EcologicalMarineUnits


def test_resolve(use_mock, scenarios, assert_identify, mocker):
    """Test the resolve method"""
    for scenario in scenarios:

        if use_mock:
            mocker.patch("requests.get", return_value=scenario.get("response"))

        # Configure
        data_source = [scenario.get("data_source")]
        resolver = Resolver(data_source)
        geometry = Geometry(scenario.get("geometry"))

        # Run
        result = resolver.resolve(geometry)

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
    resolver.data_source = [EcologicalMarineUnits()]
    assert resolver.data_source is not None
    assert isinstance(resolver.data_source, list)
    assert isinstance(resolver.data_source[0], EcologicalMarineUnits)
