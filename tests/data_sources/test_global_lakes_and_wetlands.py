"""Test the GlobalLakesAndWetlands data source"""

import zipfile
from unittest.mock import mock_open, patch
import pytest
from tests.conftest import load_geometry, load_response
from geoenv.geometry import Geometry
from geoenv.environment import Environment
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
    ecosystems = {env.data["properties"]["ecosystem"] for env in environments}
    assert ecosystems == {
        "Other permanent waterbody",
        "Riverine, seasonally saturated, forested",
    }

    # 2. Polygon with exclusion ring (donut / hole)
    hole_geom = Geometry(load_geometry("polygon_with_exclusion_ring_on_land_and_ocean"))
    hole_envs = await data_source.get_environment(hole_geom)
    assert len(hole_envs) == 1
    assert hole_envs[0].data["properties"]["ecosystem"] == "Other permanent waterbody"

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


def test_term_mapping_multi_row(monkeypatch):
    """Test applying term mapping when an ecosystem maps to multiple ENVO terms."""
    mock_tsv = (
        "subject_category\tsubject_id\tsubject_label\tpredicate_id\tobject_id\tobject_label\tconfidence\tcomment\tmapping_justification\tmapping_date\tcreator_id\n"
        "GLWD:WetlandClass\tGLWD:RiverineRegularlyFloodedForested\tRiverine, regularly flooded, forested\tskos:broadMatch\tENVO:01000921\triverine wetland\t1\tComment\tsemapv:ManualMappingCuration\t2026-08-24\thttps://orcid.org/0000-0003-2261-9931\n"
        "GLWD:WetlandClass\tGLWD:RiverineRegularlyFloodedForested\tRiverine, regularly flooded, forested\tskos:broadMatch\tENVO:00000233\tforested wetland\t1\tComment\tsemapv:ManualMappingCuration\t2026-08-24\thttps://orcid.org/0000-0003-2261-9931\n"
    )
    mock_yml = (
        "mapping_set_id: GLWD\n"
        "curie_map:\n"
        "  ENVO: http://purl.obolibrary.org/obo/ENVO_\n"
        "  GLWD: https://example.com/glwd#\n"
    )

    env = Environment(
        data={
            "dataSource": {"name": "GlobalLakesAndWetlands"},
            "properties": {"ecosystem": "Riverine, regularly flooded, forested"},
        }
    )
    geometry = Geometry(load_geometry("point_on_lake"))
    response = construct_response(
        geometry=geometry,
        environment=[env],
        identifier="test-multi-row-id",
        description="GLWD Multi-Row Test",
    )

    def fake_open(file, *args, **kwargs):
        if str(file).endswith(".tsv"):
            return mock_open(read_data=mock_tsv)()
        elif str(file).endswith(".yml"):
            return mock_open(read_data=mock_yml)()
        return open(file, *args, **kwargs)

    with patch("builtins.open", side_effect=fake_open):
        response.apply_term_mapping("ENVO")

    mapped = response.data["properties"]["environment"][0]["mappedProperties"]
    assert len(mapped) == 2
    labels = {m["label"] for m in mapped}
    assert labels == {"riverine wetland", "forested wetland"}
    uris = {m["uri"] for m in mapped}
    assert uris == {
        "http://purl.obolibrary.org/obo/ENVO_01000921",
        "http://purl.obolibrary.org/obo/ENVO_00000233",
    }


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


def test_ensure_dataset_extracts_existing_zip(tmp_path):
    """Test that an existing zip archive in cache is extracted without downloading."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    zip_path = cache_dir / "GLWD_v2_0_combined_classes_tif.zip"

    # Create a mock zip with the expected GeoTIFF
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(
            "GLWD_v2_0_combined_classes/GLWD_v2_0_main_class.tif",
            "dummy tif content",
        )

    data_source = GlobalLakesAndWetlands(cache_dir=cache_dir, auto_download=False)
    tif_path = data_source.ensure_dataset()
    assert tif_path.is_file()
    assert tif_path.name == "GLWD_v2_0_main_class.tif"
    assert tif_path.read_text() == "dummy tif content"
