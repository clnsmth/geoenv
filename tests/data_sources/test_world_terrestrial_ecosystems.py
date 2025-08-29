"""Test the WorldTerrestrialEcosystems data source"""

from importlib.resources import files
import pytest
from tests.conftest import load_geometry, load_response
from geoenv.geometry import Geometry
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.data_sources.world_terrestrial_ecosystems import (
    create_attribute_table,
    apply_code_mapping,
)


def test_init():
    """Test the DataSource class initialization"""
    data_source = WorldTerrestrialEcosystems()
    assert data_source.grid_size is None


@pytest.mark.asyncio
async def test_get_environment_with_grid_size(use_mock):
    """Test the get_environment method with grid_size set"""

    if use_mock:
        pytest.skip("Skipping test when use_mock is False")

    data_source = WorldTerrestrialEcosystems()
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))

    # Normally polygon_on_land_and_ocean geometry doesn't get_environment to
    # anything because the polygon centroid is over the ocean.
    result = await data_source.get_environment(geometry)
    assert not result

    # However, when the grid size is set, the polygon is converted to a series
    # of points that are then resolvable to the WorldTerrestrialEcosystems
    # data source.
    data_source.grid_size = 0.5
    result = await data_source.get_environment(geometry)
    assert len(result) == 1


def test_grid_size(scenarios):
    """Test the grid_size attribute of the WorldTerrestrialEcosystems data
    source."""
    for scenario in scenarios:
        if scenario.get("data_source") == WorldTerrestrialEcosystems():
            # Get
            data_source = scenario["data_sources"]
            assert data_source.grid_size is None
            # Set
            grid_size = 0.5
            data_source.grid_size = grid_size
            assert data_source.grid_size == grid_size


def test_attribute_tables(use_mock, tmp_path):
    """Test the attribute table of data sources. These need to be checked
    against the real data source to ensure that the attribute tables are
    up-to-date.
    """
    if use_mock:
        pytest.skip("Skipping test when use_mock is False")

    # Get attribute table from the data source and compare against the local
    # copy.
    create_attribute_table(output_directory=tmp_path)
    for file in tmp_path.iterdir():
        with open(file, "r", encoding="utf-8") as f:
            print(file.name)
            content = f.read()
            with open(
                files("geoenv.data.data_source_attributes").joinpath(
                    "wte_attribute_table.json"
                ),
                "r",
                encoding="utf-8",
            ) as attribute_table:
                fixture_content = attribute_table.read()
                assert content == fixture_content


def test_apply_code_mapping():
    """Test apply_code_mapping function."""

    # Positive test case - Code of a non-empty response are mapped to
    # environmental properties
    response = load_response("wte_success")
    code = response.data["properties"]["Values"][0]
    assert code == "175"
    data = apply_code_mapping(response.data)
    assert len(data["results"]) == 1
    for k, v in data["results"][0].items():
        assert isinstance(k, str)
        assert len(k) > 0
        assert isinstance(v, str)
        assert len(v) > 0

    # Negative test case - Codes of an empty response are not mapped to
    # environmental properties
    response = load_response("wte_fail")
    code = response.data["properties"]["Values"][0]
    assert code == "NoData"
    data = apply_code_mapping(response.data)
    assert data == {"results": []}
