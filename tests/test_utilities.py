"""Test the utilities module"""

import json
from importlib.resources import files

import pytest

import geoenv
from geoenv.data_sources.world_terrestrial_ecosystems import apply_code_mapping
from geoenv.geometry import Geometry
from geoenv.utilities import EnvironmentDataModel, get_properties, user_agent
from geoenv.response import Response, construct_response
from tests.conftest import load_response


def test_set_identifier():
    """Test the set_identifier adds the identifier to the data model"""

    # No identifier to start
    environment = EnvironmentDataModel()
    assert environment.data["dataSource"]["identifier"] is None

    # Identifier is present after running the method
    identifier = "Some arbitrary identifier"
    environment.set_identifier(identifier)
    assert environment.data["dataSource"]["identifier"] == identifier


def test_set_data_source():
    """Test the set_data_source adds the data_source to the data model"""

    # No data_source to start
    environment = EnvironmentDataModel()
    assert environment.data["dataSource"]["name"] is None

    # data_source is present after running the method
    data_source = "Some arbitrary data source"
    environment.set_data_source(data_source)
    assert environment.data["dataSource"]["name"] == data_source


def test_set_date_created():
    """Test the set_date_created adds the date_created to the data model"""

    # No dateCreated to start
    environment = EnvironmentDataModel()
    assert environment.data["dateCreated"] is None

    # dateCreated is present after running the method
    environment.set_date_created()
    assert environment.data["dateCreated"] is not None


def test_set_properties():
    """Test the set_properties adds the properties to the data model"""

    # No properties to start
    environment = EnvironmentDataModel()
    assert len(environment.data["properties"]) == 0

    # Properties are present after running the method
    environment.set_properties({"Some property": "Some value"})
    assert len(environment.data["properties"]) > 0


def test_data_model(empty_environment_data_model):
    """Test the EnvironmentDataModel class"""
    data_model = EnvironmentDataModel()

    # Has the correct default values
    assert data_model.data == empty_environment_data_model


def test_get_properties():
    """Test the get_properties function."""
    response = load_response("wte_success")
    response.data = apply_code_mapping(response.data)  # Create properties to fetch

    # The get_properties function should return a dictionary of attributes
    # from the response object. The dictionary should contain the requested
    # attributes.
    properties = ["Landforms", "Landcover", "Climate_Re"]
    result = get_properties(response.data, properties)
    assert isinstance(result, dict)
    for p in properties:
        assert p in result
        assert len(result[p]) > 0

    # An empty list is returned for attributes that are not present.
    result = get_properties(response.data, ["Not a valid attribute"])
    assert "Not a valid attribute" in result
    assert len(result["Not a valid attribute"]) == 0


@pytest.mark.asyncio
async def test_construct_response(scenarios, mocker, empty_data_model):
    """Test the construct_response function."""
    # Compiles a list of Environment into the data model represented by the
    # Response object and tests for expected properties

    # Create a list of Environment objects, then construct
    environments = []
    for scenario in scenarios:
        mocker.patch("requests.get", return_value=scenario.get("response"))
        data_source = scenario["data_source"]
        environment = await data_source.get_environment(Geometry(scenario["geometry"]))
        environments.extend(environment)
    identifier = "Some identifier"
    geometry = scenarios[0]["geometry"]  # Any geometry will do
    result = construct_response(Geometry(geometry), environments, identifier)

    # Top level keys are present
    assert result.data.keys() == empty_data_model.keys()
    # Identifier value matches the input
    assert result.data["identifier"] == identifier
    # Geometry value matches the input
    assert result.data["geometry"] == geometry
    # Environment is a list of environments, which are dictionaries
    assert isinstance(result.data["properties"]["environment"], list)
    # Check that the environment are a list of dictionaries
    for env in result.data["properties"]["environment"]:
        assert isinstance(env, dict)


def test_apply_term_mapping(data_model):
    """Test the apply_term_mapping method of the EnvironmentDataModel class."""
    # Remove the semantic resource terms from the test data model to set the
    # baseline for the test
    data_model.data["properties"]["environment"][0]["mappedProperties"] = []
    data = data_model

    # Apply term mapping for each environment
    data.apply_term_mapping("ENVO")

    # Check that the semantic resource terms are set for each environment, and
    # that no "sssom:NoMapping" is present
    for item in data.data["properties"]["environment"]:
        assert len(item["mappedProperties"]) > 0
        for term in item["mappedProperties"]:
            assert "sssom:nomapping" not in term["uri"].lower()


def test_apply_term_mapping_for_unrecognized_semantic_resources(data_model):
    """Test the apply_term_mapping method of the EnvironmentDataModel class
    for unrecognized semantic resources."""
    # Remove the semantic resource terms from the test data model to set the
    # baseline for the test
    data_model.data["properties"]["environment"][0]["mappedProperties"] = []

    # Apply a term mapping for an unrecognized semantic resource results in no
    # changes to the data model
    data_model.apply_term_mapping("SomeUnrecognizedSemanticResource")
    assert data_model.data["properties"]["environment"][0]["mappedProperties"] == []


def test_data_methods_of_response_class():
    """Test the data methods of the Response class."""
    # Getter
    d = {"type": "Feature"}
    data = Response({"type": "Feature"})
    assert data.data == d

    # Setter
    d = {"type": "Environment"}
    data.data = d
    assert data.data == d


def test_properties_methods_of_data_class():
    """Test the properties methods of the Data class."""
    # Getter
    data = Response({"type": "Feature"})
    assert data.properties is not None
    assert isinstance(data.properties, dict)

    # Setter
    value = {"Some property": "Some value"}
    assert data.properties != value
    data.properties = value
    assert data.properties == value


def test_data_methods_of_environment_data_model_class():
    """Test the data methods of the EnvironmentDataModel class."""
    # Getter
    environment = EnvironmentDataModel()
    assert environment.data is not None
    assert isinstance(environment.data, dict)

    # Setter
    value = {"type": "Feature"}
    assert environment.data != value
    environment.data = value
    assert environment.data == value


def test_to_schema_org(data_model):
    """Test the to_schema_org method of the EnvironmentDataModel class."""
    # Create instance of the Response object to convert to schema.org format.

    schema_org = data_model.to_schema_org()

    # Load from file
    with open(
        files("tests.data.schema_org").joinpath("schema_org.jsonld"),
        "r",
        encoding="utf-8",
    ) as f:
        expected = json.load(f)

    assert schema_org == expected


def test__to_schema_org_geo(data_model):
    """Test the _to_schema_org_geo method of the EnvironmentDataModel class."""
    # Polygon
    # pylint: disable=protected-access
    geo = data_model._to_schema_org_geo()
    assert geo == {
        "@type": "GeoCoordinates",
        "latitude": 37.905931,
        "longitude": -122.622364,
        "elevation": None,
    }

    # Point
    data_model.data["geometry"]["type"] = "Point"
    data_model.data["geometry"]["coordinates"] = [-123.552, 39.804, 0]
    # pylint: disable=protected-access
    geo = data_model._to_schema_org_geo()
    assert geo == {
        "@type": "GeoCoordinates",
        "latitude": 39.804,
        "longitude": -123.552,
        "elevation": 0,
    }

    # Other types
    data_model.data["geometry"]["type"] = "LineString"
    # pylint: disable=protected-access
    geo = data_model._to_schema_org_geo()
    assert geo is None


def test__to_schema_org_additional_property(data_model):
    """Test the _to_schema_org_additional_property method of the
    EnvironmentDataModel class."""
    # With properties
    # pylint: disable=protected-access
    additional_property = data_model._to_schema_org_additional_property()
    assert isinstance(additional_property, list)
    for item in additional_property:
        assert isinstance(item, dict)
        assert item["@type"] == "PropertyValue"
        assert "name" in item
        assert "value" in item

    # With duplicates removed
    # pylint: disable=protected-access
    data_model.data["properties"]["environment"].append(
        data_model.data["properties"]["environment"][0]
    )
    additional_property = data_model._to_schema_org_additional_property()
    for item in additional_property:
        assert additional_property.count(item) == 1

    # Without properties
    # pylint: disable=protected-access
    data = data_model
    data.data["properties"]["environment"] = []
    additional_property = data._to_schema_org_additional_property()
    assert additional_property is None


def test__to_schema_org_keywords(data_model):
    """Test the _to_schema_org_keywords method of the EnvironmentDataModel
    class."""
    # With ENVO terms
    # pylint: disable=protected-access
    keywords = data_model._to_schema_org_keywords()
    assert isinstance(keywords, list)
    for item in keywords:
        assert "@id" in item
        assert "@type" in item
        assert "name" in item
        assert "inDefinedTermSet" in item
        assert "termCode" in item

    # With duplicates removed
    # pylint: disable=protected-access
    data_model.data["properties"]["environment"].append(
        data_model.data["properties"]["environment"][0]
    )
    keywords = data_model._to_schema_org_keywords()
    for item in keywords:
        assert keywords.count(item) == 1

    # Without ENVO terms
    # pylint: disable=protected-access
    data = data_model
    data.data["properties"]["environment"] = []
    keywords = data._to_schema_org_keywords()
    assert keywords is None


def test_user_agent():
    """Test the user_agent function returns the correct User-Agent header."""
    header = user_agent()
    assert isinstance(header, dict)
    assert "user-agent" in header
    expected = (
        f"geoenv/{getattr(geoenv, '__version__', 'unknown')} "
        f"(+https://pypi.org/project/geoenv)"
    )
    assert header["user-agent"] == expected
