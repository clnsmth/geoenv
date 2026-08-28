"""Test the GlobalRiverClassification data source"""

import zipfile
import pytest
from tests.conftest import load_geometry, load_response
from geoenv.geometry import Geometry
from geoenv.data_sources import GlobalRiverClassification
from geoenv.data_sources.global_river_classification import (
    apply_code_mapping,
    get_gloric_code_mapping,
)
from geoenv.response import construct_response


def test_init():
    """Test the DataSource class initialization"""
    data_source = GlobalRiverClassification()
    assert data_source.buffer == 1.0
    assert data_source.geometry is None
    assert data_source.data is None
    assert len(data_source.properties) > 0


def test_buffer(scenarios):
    """Test the buffer property getter and setter"""
    for scenario in scenarios:
        if scenario.get("data_source") == GlobalRiverClassification():
            data_source = scenario["data_source"]
            assert data_source.buffer == 1.0
            data_source.buffer = 2.5
            assert data_source.buffer == 2.5
            data_source.buffer = None
            assert data_source.buffer is None


def test_get_gloric_code_mapping():
    """Test loading GloRiC attribute table mapping"""
    mapping = get_gloric_code_mapping()
    assert "reachTypes" in mapping
    assert "hydrologicClasses" in mapping
    assert "physioClimaticClasses" in mapping
    assert "geomorphicClasses" in mapping
    assert len(mapping["reachTypes"]) > 100


def test_apply_code_mapping():
    """Test apply_code_mapping function on GloRiC responses"""
    # Positive test case with reaches
    response = load_response("gloric_success")
    data = apply_code_mapping(response.data)
    assert "results" in data
    assert len(data["results"]) == 2
    first_result = data["results"][0]
    assert first_result["Reach_type"] == "511"
    assert "warm, high moisture region" in first_result["ClassName"]

    # Test mapping with simple Values array
    simple_data = {"properties": {"Values": ["111"]}}
    mapped_simple = apply_code_mapping(simple_data)
    assert len(mapped_simple["results"]) == 1
    assert mapped_simple["results"][0]["Reach_type"] == "111"
    assert "cold, low and medium moisture" in mapped_simple["results"][0]["ClassName"]

    # Negative test case (NoData)
    response_fail = load_response("gloric_fail")
    data_fail = apply_code_mapping(response_fail.data)
    assert data_fail["results"] == []


@pytest.mark.asyncio
async def test_get_environment_point_mocked(mocker):
    """Test get_environment on Point geometry with mocked response for offline CI"""
    data_source = GlobalRiverClassification()
    mocker.patch.object(
        data_source,
        "_request",
        mocker.AsyncMock(return_value=load_response("gloric_success").json()),
    )
    geometry = Geometry(load_geometry("point_on_river"))
    environments = await data_source.get_environment(geometry)
    assert isinstance(environments, list)
    assert len(environments) == 2
    hydr_classes = {env.data["properties"]["hydrologicClass"] for env in environments}
    assert "very small river" in hydr_classes
    ecosystems = {env.data["properties"]["ecosystem"] for env in environments}
    assert any("warm, high moisture region" in e for e in ecosystems)


@pytest.mark.asyncio
async def test_get_environment_polygon_mocked(mocker):
    """Test get_environment on Polygon geometry with mocked response for offline CI"""
    data_source = GlobalRiverClassification()
    geometry = Geometry(load_geometry("polygon_on_land"))

    # Positive mocked polygon query
    mocker.patch.object(
        data_source,
        "_request",
        mocker.AsyncMock(return_value=load_response("gloric_success").json()),
    )
    environments = await data_source.get_environment(geometry)
    assert isinstance(environments, list)
    assert len(environments) == 2

    # Negative mocked polygon query (NoData)
    mocker.patch.object(
        data_source,
        "_request",
        mocker.AsyncMock(return_value=load_response("gloric_fail").json()),
    )
    environments_fail = await data_source.get_environment(geometry)
    assert environments_fail == []


@pytest.mark.asyncio
async def test_term_mapping_envo(use_mock, mocker):
    """Test applying ENVO term mapping to GlobalRiverClassification results"""
    data_source = GlobalRiverClassification()
    if use_mock:
        mocker.patch.object(
            data_source,
            "_request",
            mocker.AsyncMock(return_value=load_response("gloric_success").json()),
        )
    geometry = Geometry(load_geometry("point_on_river"))
    environment = await data_source.get_environment(geometry)
    response = construct_response(
        geometry,
        environment,
        identifier="gloric-test",
        description="Point on river test",
    )
    response.apply_term_mapping("ENVO")

    environments = response.data["properties"]["environment"]
    assert len(environments) > 0
    first_env = environments[0]
    mapped = first_env["mappedProperties"]
    assert len(mapped) > 0
    assert any("stream" in m["label"] or "river" in m["label"] for m in mapped)
    assert any("ENVO" in m["uri"] for m in mapped)


@pytest.mark.asyncio
async def test_get_environment_direct(use_mock):
    """Test direct spatial queries on GloRiC shapefile (live test)"""
    if use_mock:
        pytest.skip("Skipping live test when use_mock is True")

    data_source = GlobalRiverClassification(buffer=1.0)

    # 1. Point on river (with 1.0 km buffer)
    river_geom = Geometry(load_geometry("point_on_river"))
    river_envs = await data_source.get_environment(river_geom)
    assert isinstance(river_envs, list)
    assert len(river_envs) > 0

    # 2. Polygon on land
    poly_geom = Geometry(load_geometry("polygon_on_land"))
    poly_envs = await data_source.get_environment(poly_geom)
    assert isinstance(poly_envs, list)
    assert len(poly_envs) > 0

    # Ensure all ecosystems are strictly unique
    ecosystems = [env.data["properties"]["ecosystem"] for env in poly_envs]
    assert len(ecosystems) == len(set(ecosystems)), (
        "Polygon query returned duplicate ecosystems"
    )

    # 3. Polygon with exclusion ring (donut / hole)
    hole_geom = Geometry(load_geometry("polygon_with_exclusion_ring_on_land_and_ocean"))
    hole_envs = await data_source.get_environment(hole_geom)
    assert isinstance(hole_envs, list)
    hole_ecosystems = [env.data["properties"]["ecosystem"] for env in hole_envs]
    assert len(hole_ecosystems) == len(set(hole_ecosystems))

    # 4. Point on ocean (should find 0 reaches)
    ocean_geom = Geometry(load_geometry("point_on_ocean"))
    ocean_envs = await data_source.get_environment(ocean_geom)
    assert len(ocean_envs) == 0


def test_ensure_dataset_missing_error(tmp_path):
    """Test ensure_dataset raises FileNotFoundError when auto_download=False and file is missing"""
    data_source = GlobalRiverClassification(
        data_path=tmp_path / "nonexistent.shp",
        cache_dir=tmp_path / "cache",
        auto_download=False,
    )
    with pytest.raises(FileNotFoundError):
        data_source.ensure_dataset()


def test_ensure_dataset_extracts_existing_zip(tmp_path):
    """Test that an existing zip archive in cache is extracted without downloading."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    zip_path = cache_dir / "GloRiC_v10_shapefile.zip"

    # Create a mock zip with the expected shapefile
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("GloRiC_v10_shapefile/GloRiC_v10.shp", "dummy shapefile content")

    data_source = GlobalRiverClassification(cache_dir=cache_dir, auto_download=False)
    shp_path = data_source.ensure_dataset()
    assert shp_path.is_file()
    assert shp_path.name == "GloRiC_v10.shp"
    assert shp_path.read_text() == "dummy shapefile content"
