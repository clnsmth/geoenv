"""Test the mock_data"""

from json import loads
import pytest
from geoenv.data_sources import (
    WorldTerrestrialEcosystems,
    EcologicalCoastalUnits,
    EcologicalMarineUnits,
    GlobalLakesAndWetlands,
    GlobalRiverClassification,
)
from tests.conftest import load_geometry
from tests.data.create_mock_data import create_mock_response_content


@pytest.mark.asyncio
async def test_mock_response_content(use_mock, tmp_path):
    """Test that live response content is structurally consistent and compatible
    with data source parsers."""

    if use_mock:
        pytest.skip("Skipping live test when use_mock is True")

    await create_mock_response_content(output_directory=tmp_path)  # fresh responses
    for file in tmp_path.iterdir():
        with open(file, "r", encoding="utf-8") as f:
            new_data = loads(f.read())
            is_success = "_success" in file.name

            if "wte_" in file.name:
                validate_wte_response(new_data, is_success)
            elif "ecu_" in file.name:
                validate_ecu_response(new_data, is_success)
            elif "emu_" in file.name:
                validate_emu_response(new_data, is_success, file.name)
            elif "glwd_" in file.name:
                validate_glwd_response(new_data, is_success)
            elif "gloric_" in file.name:
                validate_gloric_response(new_data, is_success)


def validate_wte_response(new_data: dict, is_success: bool) -> None:
    """Validate World Terrestrial Ecosystems response structure and compatibility."""
    assert isinstance(new_data, dict), "WTE response must be a JSON dictionary"

    wte = WorldTerrestrialEcosystems()
    if is_success:
        geom = load_geometry("point_on_land")
        wte.geometry = geom
        wte.data = new_data
        assert wte.has_environment(), (
            "WTE success response should indicate has_environment=True"
        )
        environments = wte.convert_data()
        assert len(environments) > 0, (
            "WTE success response should resolve at least one Environment"
        )
        for env in environments:
            assert env.data["properties"], (
                "Environment should contain non-empty properties"
            )
    else:
        geom = load_geometry("point_on_ocean")
        wte.geometry = geom
        wte.data = new_data
        assert not wte.has_environment(), (
            "WTE fail response should indicate has_environment=False"
        )
        environments = wte.convert_data()
        assert len(environments) == 0, (
            "WTE fail response should resolve no Environments"
        )


def validate_ecu_response(new_data: dict, is_success: bool) -> None:
    """Validate Ecological Coastal Units response structure and compatibility."""
    assert isinstance(new_data, dict), "ECU response must be a JSON dictionary"
    features = new_data.get("features", [])
    assert isinstance(features, list), "ECU response must contain a 'features' list"

    ecu = EcologicalCoastalUnits()
    if is_success:
        assert len(features) > 0, "ECU success response must contain features"
        for feature in features:
            props = feature.get("properties", {})
            assert "CSU_Descriptor" in props, (
                "ECU feature must contain 'CSU_Descriptor' property"
            )
            assert isinstance(props["CSU_Descriptor"], str), (
                "CSU_Descriptor must be a string"
            )
            assert len(props["CSU_Descriptor"]) > 0, "CSU_Descriptor must not be empty"

        geom = load_geometry("polygon_on_land_and_ocean")
        ecu.geometry = geom
        ecu.data = new_data
        assert ecu.has_environment(), (
            "ECU success response should indicate has_environment=True"
        )
        unique_envs = ecu.unique_environment()
        assert len(unique_envs) > 0, (
            "ECU success response should have unique environments"
        )
        environments = ecu.convert_data()
        assert len(environments) == len(unique_envs), (
            "Converted environments must match unique environments count"
        )
        for env in environments:
            assert env.data["properties"].get("ecosystem"), (
                "Environment should contain ecosystem descriptor"
            )
    else:
        assert len(features) == 0, "ECU fail response should contain 0 features"
        geom = load_geometry("polygon_on_land")
        ecu.geometry = geom
        ecu.data = new_data
        assert not ecu.has_environment(), (
            "ECU fail response should indicate has_environment=False"
        )
        assert ecu.unique_environment() == []
        assert ecu.convert_data() == []


def validate_emu_response(new_data: dict, is_success: bool, file_name: str) -> None:
    """Validate Ecological Marine Units response structure and compatibility."""
    assert isinstance(new_data, dict), "EMU response must be a JSON dictionary"
    features = new_data.get("features", [])
    assert isinstance(features, list), "EMU response must contain a 'features' list"

    emu = EcologicalMarineUnits()
    if is_success:
        assert "fields" in new_data, "EMU response must contain 'fields' metadata"
        field_names = {f["name"] for f in new_data.get("fields", []) if "name" in f}
        expected_fields = {"UnitTop", "UnitBottom", "OceanName", "Name_2018"}
        assert expected_fields.issubset(field_names), (
            f"EMU fields missing expected names: {expected_fields - field_names}"
        )

        assert len(features) > 0, "EMU success response must contain features"
        for feature in features:
            attrs = feature.get("attributes", {})
            for field in expected_fields:
                assert field in attrs, f"EMU feature attributes missing field: {field}"

        if "point_on_ocean_with_depth" in file_name:
            geom = load_geometry("point_on_ocean_with_depth")
        else:
            geom = load_geometry("polygon_on_ocean")

        emu.geometry = geom
        emu.data = new_data
        assert emu.has_environment(), (
            "EMU success response should indicate has_environment=True"
        )
        environments = emu.convert_data()
        assert len(environments) > 0, (
            "EMU success response should resolve at least one Environment"
        )
        for env in environments:
            assert env.data["properties"].get("ecosystem"), (
                "Environment should contain ecosystem descriptor"
            )
    else:
        assert len(features) == 0, "EMU fail response should contain 0 features"
        geom = load_geometry("polygon_on_land")
        emu.geometry = geom
        emu.data = new_data
        assert not emu.has_environment(), (
            "EMU fail response should indicate has_environment=False"
        )
        assert emu.convert_data() == []


def validate_glwd_response(new_data: dict, is_success: bool) -> None:
    """Validate Global Lakes and Wetlands response structure and compatibility."""
    assert isinstance(new_data, dict), "GLWD response must be a JSON dictionary"
    assert "properties" in new_data, "GLWD response must contain 'properties'"
    assert "Values" in new_data["properties"], "GLWD response must contain 'Values'"

    glwd = GlobalLakesAndWetlands()
    if is_success:
        geom = load_geometry("point_on_lake")
        glwd.geometry = geom
        glwd.data = new_data
        assert glwd.has_environment(), (
            "GLWD success response should indicate has_environment=True"
        )
        environments = glwd.convert_data()
        assert len(environments) > 0, (
            "GLWD success response should resolve at least one Environment"
        )
        for env in environments:
            assert env.data["properties"].get("ecosystem"), (
                "Environment should contain ecosystem descriptor"
            )
    else:
        geom = load_geometry("point_on_ocean")
        glwd.geometry = geom
        glwd.data = new_data
        assert not glwd.has_environment(), (
            "GLWD fail response should indicate has_environment=False"
        )
        assert glwd.convert_data() == []


def validate_gloric_response(new_data: dict, is_success: bool) -> None:
    """Validate Global River Classification response structure and compatibility."""
    assert isinstance(new_data, dict), "GloRiC response must be a JSON dictionary"
    assert "properties" in new_data, "GloRiC response must contain 'properties'"
    assert "Values" in new_data["properties"], "GloRiC response must contain 'Values'"

    gloric = GlobalRiverClassification()
    if is_success:
        geom = load_geometry("point_on_river")
        gloric.geometry = geom
        gloric.data = new_data
        assert gloric.has_environment(), (
            "GloRiC success response should indicate has_environment=True"
        )
        environments = gloric.convert_data()
        assert len(environments) > 0, (
            "GloRiC success response should resolve at least one Environment"
        )
        for env in environments:
            assert env.data["properties"].get("ecosystem"), (
                "Environment should contain ecosystem descriptor"
            )
            assert env.data["properties"].get("hydrologicClass"), (
                "Environment should contain hydrologicClass"
            )
    else:
        geom = load_geometry("point_on_ocean")
        gloric.geometry = geom
        gloric.data = new_data
        assert not gloric.has_environment(), (
            "GloRiC fail response should indicate has_environment=False"
        )
        assert gloric.convert_data() == []
