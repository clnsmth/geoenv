"""Test the GlobalLakesAndWetlands data source"""

import pytest
from tests.conftest import load_geometry, load_response
from geoenv.geometry import Geometry
from geoenv.data_sources import GlobalLakesAndWetlands
from geoenv.data_sources.global_lakes_and_wetlands import (
    apply_code_mapping,
    fetch_figshare_metadata,
)
from geoenv.response import construct_response


def test_init():
    """Test the DataSource class initialization"""
    data_source = GlobalLakesAndWetlands()
    assert data_source.grid_size is None
    assert data_source.geometry is None
    assert data_source.data is None
    assert len(data_source.properties) > 0


@pytest.mark.asyncio
async def test_get_environment_polygon_direct(use_mock):
    """Test direct raster polygon masking (zonal queries) on GLWD"""
    if use_mock:
        pytest.skip("Skipping live test when use_mock is True")

    data_source = GlobalLakesAndWetlands()

    # 1. Standard Polygon
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))
    environments = await data_source.get_environment(geometry)
    assert isinstance(environments, list)
    assert len(environments) == 2
    class_ids = {env.data["properties"]["classId"] for env in environments}
    assert class_ids == {"6", "14"}

    # 2. Polygon with exclusion ring (donut / hole)
    hole_geom = Geometry(load_geometry("polygon_with_exclusion_ring_on_land_and_ocean"))
    hole_envs = await data_source.get_environment(hole_geom)
    assert len(hole_envs) == 1
    assert hole_envs[0].data["properties"]["classId"] == "6"

    # 3. Polygon on ocean (no wetland features)
    ocean_geom = Geometry(load_geometry("polygon_on_ocean"))
    ocean_envs = await data_source.get_environment(ocean_geom)
    assert len(ocean_envs) == 0

    # 4. Out of bounds polygon (Antarctica latitude below raster extent)
    oob_geom = Geometry(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, -75.0],
                    [10.0, -75.0],
                    [10.0, -70.0],
                    [0.0, -70.0],
                    [0.0, -75.0],
                ]
            ],
        }
    )
    oob_envs = await data_source.get_environment(oob_geom)
    assert len(oob_envs) == 0


@pytest.mark.asyncio
async def test_get_environment_polygon_mocked(mocker):
    """Test get_environment on Polygon geometries using mocked response (offline CI)."""
    data_source = GlobalLakesAndWetlands()
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))

    # Positive case: multi-class polygon response
    mocker.patch.object(
        data_source,
        "_request",
        mocker.AsyncMock(return_value={"properties": {"Values": ["6", "14"]}}),
    )
    environments = await data_source.get_environment(geometry)
    assert isinstance(environments, list)
    assert len(environments) == 2
    class_ids = {env.data["properties"]["classId"] for env in environments}
    assert class_ids == {"6", "14"}
    ecosystems = {env.data["properties"]["ecosystem"] for env in environments}
    assert ecosystems == {
        "Other permanent waterbody",
        "Riverine, seasonally saturated, forested",
    }

    # Negative case: polygon with no wetlands / NoData
    mocker.patch.object(
        data_source,
        "_request",
        mocker.AsyncMock(return_value={"properties": {"Values": ["NoData"]}}),
    )
    environments_fail = await data_source.get_environment(geometry)
    assert environments_fail == []


@pytest.mark.asyncio
async def test_get_environment_with_grid_size(use_mock):
    """Test the get_environment method with grid_size set for interface parity"""
    if use_mock:
        pytest.skip("Skipping test when use_mock is True")

    data_source = GlobalLakesAndWetlands()
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))

    data_source.grid_size = 0.5
    result = await data_source.get_environment(geometry)
    assert isinstance(result, list)
    assert len(result) > 0


def test_grid_size(scenarios):
    """Test the grid_size attribute of the GlobalLakesAndWetlands data source."""
    for scenario in scenarios:
        if scenario.get("data_source") == GlobalLakesAndWetlands():
            data_source = scenario["data_source"]
            assert data_source.grid_size is None
            grid_size = 0.5
            data_source.grid_size = grid_size
            assert data_source.grid_size == grid_size


def test_apply_code_mapping():
    """Test apply_code_mapping function."""
    # Positive test case - Code of a non-empty response are mapped to
    # environmental properties
    response = load_response("glwd_success")
    code = response.data["properties"]["Values"][0]
    assert code == "1"
    data = apply_code_mapping(response.data)
    assert len(data["results"]) == 1
    assert data["results"][0]["ClassName"] == "Freshwater lake"
    assert data["results"][0]["ClassID"] == 1

    # Negative test case - Codes of an empty response are not mapped to
    # environmental properties
    response = load_response("glwd_fail")
    code = response.data["properties"]["Values"][0]
    assert code == "NoData"
    data = apply_code_mapping(response.data)
    assert data == {"results": []}


@pytest.mark.asyncio
async def test_term_mapping_envo(use_mock, mocker):
    """Test applying ENVO term mapping to GlobalLakesAndWetlands results."""
    data_source = GlobalLakesAndWetlands()
    if use_mock:
        mocker.patch.object(
            data_source,
            "_request",
            mocker.AsyncMock(return_value=load_response("glwd_success").json()),
        )
    geometry = Geometry(load_geometry("point_on_lake"))

    environments = await data_source.get_environment(geometry)
    assert len(environments) == 1

    response = construct_response(
        geometry=geometry,
        environment=environments,
        identifier="test-glwd-id",
        description="GLWD Test Point",
    )
    response.apply_term_mapping("ENVO")

    env_data = response.data["properties"]["environment"][0]
    mapped = env_data["mappedProperties"]
    assert len(mapped) > 0
    # Check that ENVO URI is present for freshwater lake
    labels = [m["label"] for m in mapped]
    uris = [m["uri"] for m in mapped]
    assert "freshwater lake" in labels
    assert any("ENVO_00000021" in u for u in uris)


def test_ensure_dataset_missing(tmp_path):
    """Test that FileNotFoundError is raised when dataset is missing and auto_download=False"""
    data_source = GlobalLakesAndWetlands(
        cache_dir=tmp_path,
        data_path=tmp_path / "non_existent.tif",
        auto_download=False,
    )
    with pytest.raises(FileNotFoundError):
        data_source.ensure_dataset()


def test_fetch_figshare_metadata():
    """Test fetch_figshare_metadata returns valid URL and checksum."""
    url, md5 = fetch_figshare_metadata()
    assert "https://" in url
    assert len(md5) == 32
