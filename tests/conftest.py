"""Configuration for the test suite"""

import os
import json
import asyncio
import tempfile
from importlib.resources import files
import pytest
from geoenv.geometry import Geometry
from geoenv.data_sources import EcologicalCoastalUnits
from geoenv.data_sources import EcologicalMarineUnits
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.response import Response, construct_response
from geoenv.utilities import EnvironmentDataModel


@pytest.fixture()
def use_mock():
    """
    Use mock data for testing purposes.

    Controlled by the GEOENV_USE_MOCK environment variable. If GEOENV_USE_MOCK
    is not set, defaults to True (use mocks). Set GEOENV_USE_MOCK to 'false'
    (case-insensitive) to disable mocks and use real HTTP requests.
    """
    value = os.environ.get("GEOENV_USE_MOCK", "true").lower()
    return value not in {"false"}


@pytest.fixture
def data_sources():
    """List of data sources to be tested."""
    return [
        EcologicalCoastalUnits(),
        EcologicalMarineUnits(),
        WorldTerrestrialEcosystems(),
    ]


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=redefined-outer-name
@pytest.fixture
def scenarios(
    raw_properties_of_ecological_coastal_units,
    raw_properties_of_ecological_marine_units,
    raw_properties_of_world_terrestrial_ecosystems,
    properties_of_ecological_coastal_units,
    properties_of_ecological_marine_units,
    properties_of_world_terrestrial_ecosystems,
):
    """List of test scenarios for each data source."""
    scenarios = [
        {  # WTE Success (Envelop on land)
            "data_source": WorldTerrestrialEcosystems(),
            "response": load_response("wte_success"),
            "geometry": load_geometry("point_on_land"),
            "unique_environment": 1,
            "has_environment": True,
            "raw_properties": raw_properties_of_world_terrestrial_ecosystems,
            "properties": properties_of_world_terrestrial_ecosystems,
            "identifier": "https://doi.org/10.5066/P9DO61LP",
        },
        {  # WTE Fail (A point over the ocean)
            "data_source": WorldTerrestrialEcosystems(),
            "response": load_response("wte_fail"),
            "geometry": load_geometry("point_on_ocean"),
            "unique_environment": 0,
            "has_environment": False,
            "raw_properties": raw_properties_of_world_terrestrial_ecosystems,
            "properties": properties_of_world_terrestrial_ecosystems,
            "identifier": "https://doi.org/10.5066/P9DO61LP",
        },
        {  # ECU Success (Envelop spanning coastal area)
            "data_source": EcologicalCoastalUnits(),
            "response": load_response("ecu_success"),
            "geometry": load_geometry("polygon_on_land_and_ocean"),
            "unique_environment": 4,
            "has_environment": True,
            "raw_properties": raw_properties_of_ecological_coastal_units,
            "properties": properties_of_ecological_coastal_units,
            "identifier": "https://doi.org/10.5066/P9HWHSPU",
        },
        {  # ECU Fail (Polygon on land)
            "data_source": EcologicalCoastalUnits(),
            "response": load_response("ecu_fail"),
            "geometry": load_geometry("polygon_on_land"),
            "unique_environment": 0,
            "has_environment": False,
            "raw_properties": raw_properties_of_ecological_coastal_units,
            "properties": properties_of_ecological_coastal_units,
            "identifier": "https://doi.org/10.5066/P9HWHSPU",
        },
        {  # EMU Success (Polygon over ocean)
            "data_source": EcologicalMarineUnits(),
            "response": load_response("emu_success"),
            "geometry": load_geometry("polygon_on_ocean"),
            "unique_environment": 7,
            "has_environment": True,
            "raw_properties": raw_properties_of_ecological_marine_units,
            "properties": properties_of_ecological_marine_units,
            "identifier": "https://doi.org/10.5066/P9Q6ZSGN",
        },
        {  # EMU Fail (Polygon on land)
            "data_source": EcologicalMarineUnits(),
            "response": load_response("emu_fail"),
            "geometry": load_geometry("polygon_on_land"),
            "unique_environment": 0,
            "has_environment": False,
            "raw_properties": raw_properties_of_ecological_marine_units,
            "properties": properties_of_ecological_marine_units,
            "identifier": "https://doi.org/10.5066/P9Q6ZSGN",
        },
    ]
    return scenarios


@pytest.fixture
def raw_properties_of_ecological_coastal_units():
    """Raw properties of Ecological Coastal Units."""
    return {
        "Slope",
        "Sinuosity",
        "Erodibility",
        "Temperature and Moisture Regime",
        "River Discharge",
        "Wave Height",
        "Tidal Range",
        "Marine Physical Environment",
        "Turbidity",
        "Chlorophyll",
        "CSU_Descriptor",
    }


@pytest.fixture
def properties_of_ecological_coastal_units():
    """Properties of Ecological Coastal Units."""
    return {
        "slope",
        "sinuosity",
        "erodibility",
        "temperatureAndMoistureRegime",
        "riverDischarge",
        "waveHeight",
        "tidalRange",
        "marinePhysicalEnvironment",
        "turbidity",
        "chlorophyll",
        "ecosystem",
    }


@pytest.fixture
def raw_properties_of_ecological_marine_units():
    """Raw properties of Ecological Marine Units."""
    return {
        "OceanName",
        "Depth",
        "Temperature",
        "Salinity",
        "Dissolved Oxygen",
        "Nitrate",
        "Phosphate",
        "Silicate",
        "EMU_Descriptor",
    }


@pytest.fixture
def properties_of_ecological_marine_units():
    """Properties of Ecological Marine Units."""
    return {
        "oceanName",
        "depth",
        "temperature",
        "salinity",
        "dissolvedOxygen",
        "nitrate",
        "phosphate",
        "silicate",
        "ecosystem",
    }


@pytest.fixture
def raw_properties_of_world_terrestrial_ecosystems():
    """Raw properties of World Terrestrial Ecosystems."""
    return {
        "Temperatur",
        "Moisture",
        "Landcover",
        "Landforms",
        "Climate_Re",
        "ClassName",
    }


@pytest.fixture
def properties_of_world_terrestrial_ecosystems():
    """Properties of World Terrestrial Ecosystems."""
    return {"temperature", "moisture", "landCover", "landForm", "climate", "ecosystem"}


@pytest.fixture
def empty_environment_data_model():
    """Empty environment data model."""
    return EnvironmentDataModel().data


@pytest.fixture
def empty_data_model():
    """Empty data model."""
    return {
        "type": "Feature",
        "identifier": None,
        "geometry": None,
        "properties": {"description": None, "environment": []},
    }


@pytest.fixture
def data_model(mocker):
    """Data model for testing purposes."""
    mocker.patch("requests.get", return_value=load_response("wte_success"))
    data_source = WorldTerrestrialEcosystems()
    geometry = Geometry(load_geometry("point_on_land"))

    environment = asyncio.get_event_loop().run_until_complete(
        data_source.get_environment(geometry)
    )
    data = construct_response(
        geometry,
        environment,
        identifier="5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
        description="Point on land",
    )
    data.apply_term_mapping()
    return data


def load_geometry(filename: str):
    """Load test geometry in JSON format."""
    with open(
        files("tests.data.geometry").joinpath(f"{filename}.json"), "r", encoding="utf-8"
    ) as f:
        return json.load(f)


def load_response(filename: str):
    """Load test response in JSON format."""
    with open(
        files("tests.data.response").joinpath(f"{filename}.json"), "r", encoding="utf-8"
    ) as f:
        if "success" in str(f):
            status_code = 200
        else:
            status_code = 404
        response = RequestsResponse(json.load(f), status_code)
        return response


# pylint: disable=too-few-public-methods
class RequestsResponse:
    """A mock object of
    https://requests.readthedocs.io/en/latest/api/#requests.Response for
    testing purposes."""

    def __init__(self, data, status_code):
        self.data = data
        self._status_code = status_code

    def json(self):
        """Return the response data."""
        return self.data

    def status_code(self):
        """Return the status code."""
        return self._status_code


@pytest.fixture
def assert_identify():
    """Assert properties and values of a successful (or unsuccessful) response
    from the resolve operation."""

    def _assert_identify(result: list, scenario: dict):
        assert isinstance(result, Response)

        # Test the geometry object
        assert isinstance(result.data["geometry"], dict)

        # Test the environment objects
        for item in result.data["properties"]["environment"]:
            assert isinstance(item, dict)

        if scenario.get("has_environment"):
            environment = result.data["properties"]["environment"]
            assert len(environment) == scenario.get("unique_environment")
            for item in environment:
                for key, value in item["properties"].items():
                    assert isinstance(key, str)
                    assert len(key) > 0
                    assert isinstance(value, str)
                    assert len(value) > 0

        # Set semantic resource terms
        env_with_terms = result.apply_term_mapping()
        assert isinstance(env_with_terms, Response)
        assert isinstance(env_with_terms.data, dict)
        environment = env_with_terms.data["properties"]["environment"]
        if len(environment) > 0:
            assert isinstance(environment[0]["mappedProperties"], list)
            for key, value in environment[0]["mappedProperties"][0].items():
                assert key in {"label", "uri"}
                assert value is not None
                if key == "uri":
                    assert value.startswith("http")

        # Write to file
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = f"{tmpdirname}/file.json"
            result.write(file_path)
            data_snapshot = result.data  # Save for comparison with read data

            # Read from file
            data = Response()
            data.read(file_path)
            assert data_snapshot == data.data
            assert isinstance(data.data, dict)

    return _assert_identify


@pytest.fixture
def assert_data_model():
    """Assert properties of the data model returned by the convert_data
    method."""

    def _assert_response_model(result: Response):
        assert isinstance(result, Response)
        assert isinstance(result.data, dict)

    return _assert_response_model


def _load_conversion_factors():
    """Load conversion factors

    Returns
    -------
    dict : conversion factors
        Dictionary of conversion factors for converting from common units of
        length to meters.
    """
    conversion_factors = {
        "meter": 1,
        "decimeter": 1e-1,
        "dekameter": 1e1,
        "hectometer": 1e2,
        "kilometer": 1e3,
        "megameter": 1e6,
        "Foot_US": 0.3048006,
        "foot": 0.3048,
        "Foot_Gold_Coast": 0.3047997,
        "fathom": 1.8288,
        "nauticalMile": 1852,
        "yard": 0.9144,
        "Yard_Indian": 0.914398530744440774,
        "Link_Clarke": 0.2011661949,
        "Yard_Sears": 0.91439841461602867,
        "mile": 1609.344,
    }
    return conversion_factors
