"""Test the mock_data"""

from json import loads, dumps
from importlib.resources import files
import pytest
from tests.data.create_mock_data import create_mock_response_content


@pytest.mark.asyncio
async def test_mock_response_content(use_mock, tmp_path):
    """Test the mock response content is consistent with new response data"""

    if use_mock:
        pytest.skip("Skipping test when use_mock is False")

    await create_mock_response_content(output_directory=tmp_path)  # fresh responses
    for file in tmp_path.iterdir():
        with open(file, "r", encoding="utf-8") as f:
            print(file.name)
            new = f.read()
            mock_file = files("tests.data.response").joinpath(file.name)
            with open(mock_file, "r", encoding="utf-8") as mf:
                mock = mf.read()

                # Remove non-deterministic (and irrelevant) components
                # response data to address fragility of tests
                if "wte_" in file.name:  # World Terrestrial Ecosystems
                    new = get_wte_properties(new)
                    mock = get_wte_properties(mock)
                elif "ecu_" in file.name:  # Ecological Coastal Units
                    new = get_ecu_properties(new)
                    mock = get_ecu_properties(mock)
                elif "emu_" in file.name:  # Ecological Marine Units
                    new = get_emu_properties(new)
                    mock = get_emu_properties(mock)

                # Compare the content
                if "ecu_" in file.name:  # ECU has some non-determinism
                    handle_ecu_nondeterminism(new, mock)
                else:
                    assert new == mock


def get_wte_properties(json_data: str) -> str:
    """Get the properties from the World Terrestrial Ecosystems response

    :param json_data: The raw response data as a JSON string
    :note: This comparison is predicated on the response properties of
    interest, which are defined in `apply_code_mapping` of the
    world_terrestrial_ecosystems module."""
    data = loads(json_data)
    properties = data.get("properties", {})
    return dumps(properties, indent=4)


def get_ecu_properties(json_data: str) -> str:
    """Get the properties from the Ecological Coastal Units response

    :param json_data: The raw response data as a JSON string
    :note: This comparison is predicated on the response properties of
    interest, which are defined in `set_properties` of the
    ecological_coastal_units module."""
    properties = []
    data = loads(json_data)
    for feature in data.get("features", []):
        descriptor = feature.get("properties", {}).get("CSU_Descriptor")
        properties.append({"CSU_Descriptor": descriptor})
    return dumps(properties, indent=4)


def get_emu_properties(json_data: str) -> str:
    """Get the properties from the Ecological Marine Units response

    :param json_data: The raw response data as a JSON string
    :note: This comparison is predicated on the response properties of
    interest, which are defined in `convert_codes_to_values` of the
    ecological_marine_units module."""
    properties = []
    data = loads(json_data)
    for feature in data.get("features", []):
        ocean = feature.get("attributes", {}).get("OceanName")
        descriptor = feature.get("attributes", {}).get("Name_2018")
        properties.append({"OceanName": ocean, "Name_2018": descriptor})
    return dumps(properties, indent=4)


def handle_ecu_nondeterminism(new: str, mock: str) -> None:
    """
    Compare new and mock Ecological Coastal Units response data, accounting
    for non-deterministic changes.

    This test was flaky because real HTTP responses for Ecological Coastal
    Units sometimes change slightly (e.g., "sloping" vs "steeply sloping" in
    CSU_Descriptor), causing snapshot comparison failures. Presumably this is
    occurring due to variance in the ECU data sources' query precision.


    To address this, the function compares the length of the new and mock
    lists and checks that each CSU_Descriptor value is in a known set of
    possible values, making the test less brittle to minor, expected changes.

    :param new: The new response data as a JSON string.
    :param mock: The mock response data as a JSON string.
    """

    mock_list = loads(mock)
    new_list = loads(new)

    possible_descriptor_values = {str(item) for item in mock_list}

    assert len(new_list) == len(mock_list)
    for item in new_list:
        assert str(item) in possible_descriptor_values
