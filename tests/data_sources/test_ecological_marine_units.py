"""Test the EcologicalMarineUnits data source"""

from json import loads
from tests.conftest import load_response, load_geometry
from geoenv.data_sources import EcologicalMarineUnits


def test_convert_codes_to_values():
    """Test the convert_codes_to_values method

    Codes listed in the response object should be converted to their string
    value equivalents."""

    # Successful response from the EMU data source
    data_source = EcologicalMarineUnits()
    data_source.data = load_response("emu_success").json()
    # Codes are numeric values initially
    for feature in data_source.data.get("features"):
        assert isinstance(feature.get("attributes").get("Name_2018"), int)
        assert isinstance(feature.get("attributes").get("OceanName"), int)
    # Codes are strings after conversion
    data_source.convert_codes_to_values()
    for feature in data_source.data.get("features"):
        assert isinstance(feature.get("attributes").get("Name_2018"), str)
        assert isinstance(feature.get("attributes").get("OceanName"), str)

    # Unsuccessful response from the EMU data source
    data_source = EcologicalMarineUnits()
    data_source.data = load_response("emu_fail").json()
    # The response is an empty list
    assert isinstance(data_source.data.get("features"), list)
    assert len(data_source.data.get("features")) == 0


def test_get_environments_for_geometry_z_values():
    """Test the get_environments_for_geometry method.

    When a geometry has a single z value (i.e. discrete depth) the
    get_environments_for_geometry_z_values method should return any EMUs
    intersecting with the z value, including both bounding EMUs when the z
    value equals the boundary between the 2 EMUs. When a geometry has 2 z
    values (i.e. range of depths) the method should return any EMUs
    intersecting with the range, including both bounding EMUs when the z value
    equals the boundary between the 2 EMUs. When a geometry has no z values
    (i.e. no depth) the method should return all EMUs.

    Rather than using a set of geographic coverage fixtures, each exemplifying
    the scenarios, we reduce the number of API calls to the EMU server by
    modifying the z values of the response objects geometry property.

    The results of the assertions were determined by visual inspection of the
    EMU server map service interface at the geographic coverage represented in
    the test fixture. Or rather the test fixture was set based on a specific
    data point in the EMU server map service interface.
    """

    # A set of tests on a point location with z values
    data_source = EcologicalMarineUnits()
    data_source.data = load_response("emu_success_point_on_ocean_with_depth").json()
    data_source.geometry = load_geometry("point_on_ocean_with_depth")

    # Single z value within EMU returns one EMU
    environments = data_source.get_environments_for_geometry_z_values(data_source.data)
    expected_environments = {18}
    assert isinstance(environments, list)
    for environment in environments:
        assert isinstance(environment, str)
        assert loads(environment)["attributes"]["Name_2018"] in expected_environments
    assert len(environments) == 1

    # Single z value on the border between two EMUs returns two EMUs
    data_source.geometry["coordinates"][2] = -30
    environments = data_source.get_environments_for_geometry_z_values(data_source.data)
    expected_environments = {18, 24}
    assert isinstance(environments, list)
    for environment in environments:
        assert isinstance(environment, str)
        assert loads(environment)["attributes"]["Name_2018"] in expected_environments
    assert len(environments) == 2

    # No z values returns all EMUs.
    data_source.geometry["coordinates"][2] = None
    environments = data_source.get_environments_for_geometry_z_values(data_source.data)
    expected_environments = {18, 24, 11, 26, 8, 19}
    assert isinstance(environments, list)
    for environment in environments:
        assert isinstance(environment, str)
        assert loads(environment)["attributes"]["Name_2018"] in expected_environments
    assert len(environments) == 6
