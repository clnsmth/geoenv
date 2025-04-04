"""Test the geometry module."""

import json
from io import StringIO
import pandas as pd
import geopandas as gpd
import pytest
import shapely
from geoenv.geometry import Geometry, grid_sample_polygon
from tests.conftest import load_geometry


def test_geometry_init():
    """Test Environment class initialization has the expected attributes."""
    geometry = Geometry(load_geometry("point_on_land"))  # any valid geometry
    assert isinstance(geometry.data, dict)


def test_geometry_type():
    """Test the geometry_type() function."""
    # Point
    geometry = Geometry(load_geometry("point_on_land"))
    assert geometry.geometry_type() == "Point"
    # Polygon
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))
    assert geometry.geometry_type() == "Polygon"
    # Unknown
    geometry = Geometry(load_geometry("point_on_land"))
    del geometry.data["type"]
    assert geometry.geometry_type() is None


def test_is_supported():
    """Test the is_supported() function."""
    # Point geometry
    geometry = Geometry(load_geometry("point_on_land"))
    assert geometry.is_supported() is True

    # Polygon geometry
    geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))
    assert geometry.is_supported() is True

    # Unsupported geometry
    assert Geometry({"type": "Unknown"}).is_supported() is False


def test_point_to_polygon():
    """Test the point_to_polygon() function.

    The point_to_polygon() function should return an ESRI envelope
    as a JSON string and have a spatial reference of 4326. If a buffer argument
    is not passed, the resulting envelope bounds should equal the point. If a
    buffer argument is passed, the resulting envelope should enclose the point
    within its bounds.
    """
    # With a buffer
    input_geometry = load_geometry("point_on_land_expands_to_coast")
    geometry = Geometry(input_geometry)
    result = geometry.point_to_polygon(buffer=0.5)
    assert isinstance(result, dict)
    assert result["type"] == "Polygon"
    assert result != input_geometry

    # Without a buffer
    input_geometry = load_geometry("point_on_land_expands_to_coast")
    geometry = Geometry(input_geometry)
    result = geometry.point_to_polygon()
    assert result == geometry.data

    # Non-point geometry inputs are unchanged
    input_geometry = load_geometry("polygon_with_exclusion_ring_on_land_and_ocean")
    geometry = Geometry(input_geometry)
    result = geometry.point_to_polygon()
    assert result["type"] == "Polygon"
    assert result == geometry.data

    # Geometry.data is not changed by point_to_polygon
    input_geometry = load_geometry("point_on_land")
    geometry = Geometry(input_geometry)
    result = geometry.point_to_polygon(buffer=0.5)
    assert geometry.data != result


def test_to_esri():
    """Test the to_esri() function."""
    # GeoJSON point to ESRI point
    point = Geometry(load_geometry("point_on_land"))
    result = point.to_esri()
    assert result["geometry"] == {
        "x": -122.622364,
        "y": 37.905931,
        "z": None,
        "spatialReference": {"wkid": 4326},
    }
    assert result["geometryType"] == "esriGeometryPoint"

    # GeoJSON point with z value to ESRI point with z value
    point = Geometry(load_geometry("point_on_ocean"))
    result = point.to_esri()
    assert result["geometry"] == {
        "x": -122.76,
        "y": 37.774,
        "z": -100.0,
        "spatialReference": {"wkid": 4326},
    }

    # GeoJSON polygon (triangle) to ESRI polygon
    polygon = Geometry(load_geometry("polygon_on_land_and_ocean"))
    result = polygon.to_esri()
    assert result["geometry"] == {
        "rings": [
            [
                [-123.8, 39.312],
                [-123.8222818, 39.3141049],
                [-123.8166231, 39.2943269],
                [-123.8, 39.312],
            ]
        ],
        "spatialReference": {"wkid": 4326},
    }
    assert result["geometryType"] == "esriGeometryPolygon"

    # GeoJSON polygon (rectangle) to ESRI polygon
    polygon = Geometry(load_geometry("polygon_on_land"))
    result = polygon.to_esri()
    assert result["geometry"] == {
        "rings": [
            [
                [-123.552, 39.804],
                [-120.83, 39.804],
                [-120.83, 40.441],
                [-123.552, 40.441],
                [-123.552, 39.804],
            ]
        ],
        "spatialReference": {"wkid": 4326},
    }
    assert result["geometryType"] == "esriGeometryPolygon"

    # Unrecognized geometry to ESRI envelope issues an error
    with pytest.raises(ValueError):
        Geometry({"type": "Unknown"}).to_esri()


def test_grid_sample_polygon():
    """Test the grid_sample_polygon() function."""
    # A simple polygon
    polygon = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
    }
    geo_series = gpd.GeoSeries.from_file(StringIO(json.dumps(polygon)))

    # Sample the polygon
    grid_size = 0.5
    representative_points = geo_series.apply(grid_sample_polygon, args=(grid_size,))

    # Representative points are midpoints of each grid cell
    assert isinstance(representative_points, pd.DataFrame)
    assert len(representative_points.columns) == 4
    for item in representative_points.items():
        point = item[1][0]
        assert isinstance(point, shapely.Point)
        assert point in [
            shapely.Point(0.25, 0.25),
            shapely.Point(0.25, 0.75),
            shapely.Point(0.75, 0.25),
            shapely.Point(0.75, 0.75),
        ]


def test_polygon_to_points():
    """Test the polygon_to_points() function."""
    polygon = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
    }
    geometry = Geometry(polygon)
    points = geometry.polygon_to_points(grid_size=0.5)
    assert isinstance(points, list)
    assert len(points) == 8  # 4 midpoints + 4 vertices
    for item in points:
        assert item["type"] == "Point"
        assert isinstance(item["coordinates"][0], float)


def test_data():
    """Test the data attribute."""
    geometry = Geometry(load_geometry("point_on_land"))
    # Get
    assert geometry.data is not None
    # Set
    default_value = geometry.data
    geometry.data = {"test": "test"}
    assert geometry.data != default_value
