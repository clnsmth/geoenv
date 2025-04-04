"""
*geometry.py*
"""

import json
from io import StringIO
from json import dumps

import daiquiri
import geopandas as gpd
import shapely
from shapely import Polygon, Point
import numpy as np

logger = daiquiri.getLogger(__name__)


class Geometry:
    """
    The Geometry class manages spatial geometries in GeoJSON format and
    provides utilities for transformation and spatial processing.

    Currently, the ``geometry`` parameter only supports GeoJSON ``Point`` and
    ``Polygon`` types, with plans to support additional types, including
    ``GeometryCollection``, in the future.
    """

    def __init__(self, geometry: dict):
        """
        Initializes a Geometry object with the given GeoJSON geometry.

        :param geometry: A dictionary representing a GeoJSON geometry.
        """
        self._data = geometry

    @property
    def data(self) -> dict:
        """
        Retrieves the stored geometry data.

        :return: A dictionary representing the GeoJSON geometry.
        """
        return self._data

    @data.setter
    def data(self, geometry: dict):
        """
        Updates the geometry data.

        :param geometry: A dictionary representing a new GeoJSON geometry.
        """
        self._data = geometry

    def is_supported(self) -> bool:
        """
        Checks if the stored geometry is supported by the resolver.
        A valid geometry must be a GeoJSON object with a top-level ``type`` of
        either "Point" or "Polygon".

        :return: ``True`` if the geometry is supported, otherwise ``False``.
        """
        logger.debug(f"Checking if geometry type '{self.geometry_type()}' is supported")
        if self.geometry_type() in ["Point", "Polygon"]:
            return True
        logger.warning(f"Unsupported geometry type: {self.geometry_type()}")
        return False

    def to_esri(self) -> dict:
        """
        Converts the GeoJSON geometry to an Esri-compatible format.

        :return: A dictionary representing the Esri-formatted geometry.
        """
        logger.debug(
            f"Converting geometry of type '{self.geometry_type()}' to Esri " f"format"
        )

        if self.geometry_type() == "Point":
            x, y, *z = self.data["coordinates"]
            geometry = {
                "x": x,
                "y": y,
                "z": z[0] if z else None,
                "spatialReference": {"wkid": 4326},
            }
            esri_geometry_type = "esriGeometryPoint"
            logger.debug("Successfully converted Point geometry to Esri format")
            return {"geometry": geometry, "geometryType": esri_geometry_type}
        if self.geometry_type() == "Polygon":
            geometry = {
                "rings": self.data["coordinates"],
                "spatialReference": {"wkid": 4326},
            }
            esri_geometry_type = "esriGeometryPolygon"
            logger.debug("Successfully converted Polygon geometry to Esri format")
            return {"geometry": geometry, "geometryType": esri_geometry_type}
        raise ValueError("Invalid geometry type")

    def geometry_type(self) -> str:
        """
        Retrieves the type of the stored geometry (e.g., "Point" or "Polygon").

        :return: A string representing the geometry type.
        """
        return self.data.get("type")

    def point_to_polygon(self, buffer=None) -> dict:
        """
        Converts a ``Point`` geometry into a ``Polygon`` by buffering it.

        :param buffer: The buffer distance used to create the polygon
            (optional).
        :return: A dictionary representing the buffered polygon in GeoJSON
            format.
        """
        if self.geometry_type() != "Point" or buffer is None:
            logger.warning(
                f"Skipping point-to-polygon conversion. Geometry type "
                f"'{self.geometry_type()}' is not a Point, or no buffer "
                f"provided."
            )
            return self.data

        logger.debug(f"Converting Point to Polygon with buffer {buffer} km")

        # pylint: disable=broad-exception-caught
        try:
            point = gpd.GeoSeries.from_file(StringIO(dumps(self.data)))
            point = point.to_crs(32634)  # A CRS in units of meters
            expanded_point = point.geometry.buffer(buffer * 1000)  # buffer to meters
            expanded_point = expanded_point.to_crs(4326)  # Convert back to EPSG:4326
            bounds = expanded_point.bounds
            polygon = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [bounds.minx[0], bounds.miny[0]],
                        [bounds.maxx[0], bounds.miny[0]],
                        [bounds.maxx[0], bounds.maxy[0]],
                        [bounds.minx[0], bounds.maxy[0]],
                        [bounds.minx[0], bounds.miny[0]],
                    ]
                ],
            }
            logger.debug(
                f"Successfully converted Point to Polygon with buffer " f"{buffer} km"
            )
            return polygon
        except Exception as e:
            logger.error(f"Failed to convert Point to Polygon: {e}", exc_info=True)
            return self.data

    def polygon_to_points(self, grid_size) -> list[dict]:
        """
        Converts a ``Polygon`` geometry into a set of representative points
        using grid-based sampling.

        :param grid_size: The size of the grid cells used for sampling.
        :return: A list of dictionaries representing sampled points in GeoJSON
            format.
        """
        if self.geometry_type() != "Polygon":
            logger.warning(
                f"Skipping polygon-to-points conversion. Geometry type "
                f"'{self.geometry_type()}' is not a Polygon."
            )
            return self.data

        # pylint: disable=broad-exception-caught
        try:
            # Get points from within the polygon
            polygon = gpd.GeoSeries.from_file(StringIO(dumps(self.data)))
            representative_points = polygon.apply(
                grid_sample_polygon, args=(grid_size,)
            )
            points = []
            for item in representative_points.items():
                geojson = json.loads(gpd.GeoSeries(item[1]).to_json())
                result = geojson["features"][0]["geometry"]
                points.append(result)
            logger.debug(
                f"Extracted {len(points)} representative points from the " f"polygon"
            )

            # Get points from the vertices of the polygon
            coords = list(polygon[0].exterior.coords)
            polygon_vertices = gpd.GeoSeries([Point(x, y) for x, y in coords])
            polygon_vertices = polygon_vertices.drop_duplicates()
            for item in polygon_vertices.items():
                geojson = json.loads(gpd.GeoSeries(item[1]).to_json())
                result = geojson["features"][0]["geometry"]
                points.append(result)

            logger.debug(f"Successfully converted Polygon to {len(points)} points")
            return points

        except Exception as e:
            logger.error(f"Failed to convert Polygon to points: {e}", exc_info=True)
            return self.data


# pylint: disable=too-many-locals
def grid_sample_polygon(polygon: shapely.Polygon, grid_size: float) -> gpd.GeoSeries:
    """
    Generates a set of representative points within a polygon using grid-based
    sampling.

    :param polygon: A Shapely Polygon object.
    :param grid_size: The size of the grid cells in the same units as the
        polygon's coordinates.
    :return: A GeoSeries of Shapely Point objects representing the sample
        points.
    """
    logger.debug(f"Starting grid sampling for polygon with grid size " f"{grid_size}")

    # pylint: disable=broad-exception-caught
    try:
        min_x, min_y, max_x, max_y = polygon.bounds
        logger.debug(
            f"Polygon bounds: min_x={min_x}, min_y={min_y}, "
            f"max_x={max_x}, max_y={max_y}"
        )
        cols = np.arange(min_x, max_x + grid_size, grid_size)
        rows = np.arange(min_y, max_y + grid_size, grid_size)

        grid_cells = []
        for x in cols:
            for y in rows:
                grid_cell = Polygon(
                    [
                        (x, y),
                        (x + grid_size, y),
                        (x + grid_size, y + grid_size),
                        (x, y + grid_size),
                    ]
                )
                grid_cells.append(grid_cell)
        logger.debug(f"Generated {len(grid_cells)} grid cells")

        grid_gdf = gpd.GeoDataFrame(geometry=grid_cells)
        intersecting_cells = grid_gdf[grid_gdf.intersects(polygon)]
        logger.debug(
            f"{len(intersecting_cells)} grid cells intersect with " f"the polygon"
        )

        sample_points = intersecting_cells.centroid
        sample_points = sample_points[sample_points.within(polygon)]
        logger.debug(
            f"Generated {len(sample_points)} sample points within the " f"polygon"
        )

        return sample_points
    except Exception as e:
        logger.error(f"Failed to generate sample points: {e}", exc_info=True)
        return gpd.GeoSeries()
