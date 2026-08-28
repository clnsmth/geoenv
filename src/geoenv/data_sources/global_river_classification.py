"""
*global_river_classification.py*
"""

import json
import os
import urllib.request
import zipfile
from importlib.resources import files
from json import dumps, loads
from pathlib import Path
from typing import List, Optional, Tuple, Union

import daiquiri
import pyogrio
import shapely.geometry
from geoenv.data_sources.data_source import DataSource
from geoenv.environment import Environment
from geoenv.geometry import Geometry
from geoenv.utilities import EnvironmentDataModel

logger = daiquiri.getLogger(__name__)

GLORIC_DOWNLOAD_URL = (
    "https://data.hydrosheds.org/file/hydrosheds-associated/gloric/"
    "GloRiC_v10_shapefile.zip"
)
DEFAULT_SHP_NAME = "GloRiC_v10.shp"


class GlobalRiverClassification(DataSource):
    """
    A concrete implementation of ``DataSource`` that retrieves river reach
    environmental classifications from the Global River Classification
    (GloRiC v1.0) dataset (Ouellet Dallaire et al. 2019).

    GloRiC classifies all river reaches globally into distinct river types
    based on hydrologic, physio-climatic, and geomorphic characteristics derived
    from HydroRIVERS and HydroATLAS.

    **Note**
        - For ``Point`` geometries, setting the ``buffer`` parameter converts
          them into a search zone of a given radius (in kilometers) before
          resolution. All overlapping river reaches within the buffered area
          are resolved and returned.
        - For ``Polygon`` geometries, all river reaches that spatially
          intersect the polygon boundary are resolved and returned as unique
          environmental classifications.

    **Further Information**
        - **Spatial Resolution**: Global coverage at 15 arc-seconds (~500 m).
        - **Coverage**: 8.5 million river reaches globally (35.9 million km).
        - **Classification**: 127 combined river reach types, 15 hydrologic
          classes, 24 physio-climatic classes, and 4 geomorphic classes.
        - **Explore the Dataset**:
          `https://www.hydrosheds.org/products/gloric
          <https://www.hydrosheds.org/products/gloric>`_.

    **Citation**
        Ouellet Dallaire, C., Lehner, B., Sayre, R., Thieme, M. (2019).
        A multidisciplinary framework to derive global river reach
        classifications at high spatial resolution. Environmental Research
        Letters, 14(2): 024003. `https://doi.org/10.1088/1748-9326/aad8e9
        <https://doi.org/10.1088/1748-9326/aad8e9>`_.
    """

    def __init__(
        self,
        buffer: Optional[float] = 1.0,
        data_path: Optional[Union[str, Path]] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        auto_download: bool = True,
    ):
        """
        Initializes the GlobalRiverClassification data source.

        :param buffer: Distance in kilometers to buffer ``Point`` geometries
            (default is 1.0 km). Set to ``None`` to disable buffering.
        :param data_path: Optional explicit path to the local ``GloRiC_v10.shp``
            file. Overrides automatic cache lookup.
        :param cache_dir: Optional custom directory to store the downloaded
            dataset. Defaults to ``~/.cache/geoenv/gloric_v1``.
        :param auto_download: Whether to automatically download the GloRiC
            dataset if it is not found locally (default is ``True``).
        """
        super().__init__()
        self._geometry = None
        self._data = None
        self._properties = {
            "Reach_type": None,
            "ClassName": None,
            "Class_hydr": None,
            "Class_phys": None,
            "Class_geom": None,
        }
        self._buffer = buffer
        self._auto_download = auto_download

        if cache_dir is not None:
            self._cache_dir = Path(cache_dir)
        else:
            base_cache = os.environ.get(
                "GEOENV_CACHE_DIR", str(Path.home() / ".cache" / "geoenv")
            )
            self._cache_dir = Path(base_cache) / "gloric_v1"

        if data_path is not None:
            self._data_path = Path(data_path)
        else:
            env_path = os.environ.get("GEOENV_GLORIC_DATA_PATH")
            self._data_path = Path(env_path) if env_path else None

    @property
    def geometry(self) -> dict:
        return self._geometry

    @geometry.setter
    def geometry(self, geometry: dict):
        self._geometry = geometry

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, data: dict):
        self._data = data

    @property
    def properties(self) -> dict:
        return self._properties

    @properties.setter
    def properties(self, properties: dict):
        self._properties = properties

    @property
    def buffer(self) -> Optional[float]:
        """
        Retrieves the buffer distance used for spatial resolution.

        :return: The buffer radius as a float in **kilometers**, or ``None``.
        """
        return self._buffer

    @buffer.setter
    def buffer(self, buffer: Optional[float]):
        """
        Sets the buffer distance used for spatial resolution.

        :param buffer: The buffer distance in **kilometers** as a float.
        """
        self._buffer = buffer

    @property
    def data_path(self) -> Optional[Path]:
        """Path to the local GloRiC shapefile."""
        return self._data_path

    @data_path.setter
    def data_path(self, path: Optional[Union[str, Path]]):
        self._data_path = Path(path) if path is not None else None

    @property
    def cache_dir(self) -> Path:
        """Directory used for caching downloaded GloRiC data."""
        return self._cache_dir

    def ensure_dataset(self) -> Path:
        """
        Ensures the GloRiC shapefile is present locally, downloading and
        extracting it if necessary.

        :return: Absolute ``Path`` to ``GloRiC_v10.shp``.
        :raises FileNotFoundError: If the shapefile is missing and
            ``auto_download`` is ``False``.
        """
        if self._data_path is not None and self._data_path.is_file():
            return self._data_path

        # Check default cache locations
        candidate = self._cache_dir / "GloRiC_v10_shapefile" / DEFAULT_SHP_NAME
        if candidate.is_file():
            self._data_path = candidate
            return self._data_path

        direct_candidate = self._cache_dir / DEFAULT_SHP_NAME
        if direct_candidate.is_file():
            self._data_path = direct_candidate
            return self._data_path

        # Check recursively in cache_dir
        if self._cache_dir.is_dir():
            for p in self._cache_dir.rglob(DEFAULT_SHP_NAME):
                if p.is_file():
                    self._data_path = p
                    return self._data_path

        # Check if an existing zip archive is in cache_dir and can be extracted
        zip_path = self._cache_dir / "GloRiC_v10_shapefile.zip"
        if zip_path.is_file() and zipfile.is_zipfile(zip_path):
            logger.info(f"Found existing GloRiC archive at {zip_path}. Extracting...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self._cache_dir)

            for p in self._cache_dir.rglob(DEFAULT_SHP_NAME):
                if p.is_file():
                    self._data_path = p
                    return self._data_path

        if not self._auto_download:
            raise FileNotFoundError(
                f"GloRiC dataset '{DEFAULT_SHP_NAME}' not found at "
                f"{self._data_path or self._cache_dir}. Set auto_download=True "
                f"or download manually."
            )

        downloaded_path = download_dataset(cache_dir=self._cache_dir)
        self._data_path = downloaded_path
        return self._data_path

    async def get_environment(self, geometry: Geometry) -> List[Environment]:
        """
        Resolves the given ``Geometry`` to river reach classifications.

        :param geometry: The geospatial geometry to resolve.
        :return: A list of ``Environment`` instances matching the geometry.
        """
        logger.debug(f"Starting get_environment in {self.__class__.__name__}")
        self.geometry = geometry
        self.data = await self._request(None, geometry)

        if not self.has_environment():
            return []

        return self.convert_data()

    async def _request(self, session, geometry: Union[Geometry, dict]) -> dict:
        """
        Queries the local GloRiC shapefile for the given geometry.

        :param session: Unused session parameter for DataSource interface parity.
        :param geometry: The Geometry object or GeoJSON dict to query.
        :return: Dictionary structured as ``{"properties": {"Values": [...], "reaches": [...]}}``.
        """
        nodata_response = {"properties": {"Values": ["NoData"]}}
        try:
            shp_file = self.ensure_dataset()
        except FileNotFoundError as e:
            logger.warning(f"Could not load GloRiC dataset: {e}")
            return nodata_response

        geom_data, geom_type = self._parse_geometry(geometry)
        if geom_type == "Point":
            if self.buffer is not None and self.buffer > 0:
                logger.debug(f"Applying buffer of {self.buffer} km to Point geometry")
                buffered_geom = Geometry(geom_data).point_to_polygon(buffer=self.buffer)
                return self._query_polygon(shp_file, buffered_geom)
            return self._query_point(shp_file, geom_data)

        if geom_type == "Polygon":
            return self._query_polygon(shp_file, geom_data)

        if geom_type is not None:
            logger.warning(f"Unsupported geometry type '{geom_type}'")
        return nodata_response

    @staticmethod
    def _parse_geometry(
        geometry: Union[Geometry, dict],
    ) -> Tuple[Optional[dict], Optional[str]]:
        """Extracts GeoJSON dictionary and geometry type from input."""
        if isinstance(geometry, Geometry):
            return geometry.data, geometry.geometry_type()
        if isinstance(geometry, dict):
            return geometry, geometry.get("type")
        logger.warning(f"Unsupported geometry object type '{type(geometry)}'")
        return None, None

    @staticmethod
    def _query_point(shp_file: Path, geom_data: dict) -> dict:
        """Queries river reaches intersecting a single exact point."""
        coords = geom_data.get("coordinates", [])
        if len(coords) < 2:
            return {"properties": {"Values": ["NoData"]}}

        x, y = float(coords[0]), float(coords[1])
        pt = shapely.geometry.Point(x, y)
        bbox = (x, y, x, y)
        try:
            df = pyogrio.read_dataframe(
                shp_file,
                bbox=bbox,
                columns=[
                    "Reach_ID",
                    "Reach_type",
                    "Class_hydr",
                    "Class_phys",
                    "Class_geom",
                    "Length_km",
                    "Log_Q_avg",
                ],
            )
            if len(df) == 0:
                return {"properties": {"Values": ["NoData"]}}

            intersecting = df[df.geometry.intersects(pt)]
            if len(intersecting) == 0:
                return {"properties": {"Values": ["NoData"]}}

            unique_values = sorted(list(set(intersecting["Reach_type"].astype(str))))
            reaches = intersecting.drop(columns=["geometry"], errors="ignore").to_dict(
                orient="records"
            )
            return {
                "properties": {
                    "Values": unique_values,
                    "reaches": reaches,
                }
            }
        except Exception as e:
            logger.error(
                f"Failed to query GloRiC shapefile for point: {e}",
                exc_info=True,
            )
            return {"properties": {"Values": ["NoData"]}}

    @staticmethod
    def _query_polygon(shp_file: Path, geom_data: dict) -> dict:
        """Queries river reaches intersecting a polygon."""
        try:
            poly = shapely.geometry.shape(geom_data)
            bbox = poly.bounds
            df = pyogrio.read_dataframe(
                shp_file,
                bbox=bbox,
                columns=[
                    "Reach_ID",
                    "Reach_type",
                    "Class_hydr",
                    "Class_phys",
                    "Class_geom",
                    "Length_km",
                    "Log_Q_avg",
                ],
            )
            if len(df) == 0:
                return {"properties": {"Values": ["NoData"]}}

            intersecting = df[df.geometry.intersects(poly)]
            if len(intersecting) == 0:
                return {"properties": {"Values": ["NoData"]}}

            unique_values = sorted(list(set(intersecting["Reach_type"].astype(str))))
            reaches = intersecting.drop(columns=["geometry"], errors="ignore").to_dict(
                orient="records"
            )
            return {
                "properties": {
                    "Values": unique_values,
                    "reaches": reaches,
                }
            }
        except ValueError:
            logger.debug("Polygon geometry does not overlap GloRiC dataset")
        except Exception as e:
            logger.error(
                f"Failed to query GloRiC shapefile for polygon: {e}",
                exc_info=True,
            )
        return {"properties": {"Values": ["NoData"]}}

    def convert_data(self) -> List[Environment]:
        """
        Converts raw data from the data source into a list of standardized
        ``Environment`` instances.

        :return: A list of ``Environment`` objects.
        """
        logger.debug(f"Starting data conversion in {self.__class__.__name__}")
        result = []
        unique_gloric_environments = self.unique_environment()
        for unique_env in unique_gloric_environments:
            environment = EnvironmentDataModel()
            environment.set_identifier("https://doi.org/10.1088/1748-9326/aad8e9")
            environment.set_data_source(self.__class__.__name__)
            environment.set_date_created()
            environment.set_properties(unique_env)
            result.append(Environment(data=environment.data))
            logger.debug("Converted environment properties")
        logger.debug(
            f"Successfully converted {len(result)} environments in "
            f"{self.__class__.__name__}"
        )
        return result

    def unique_environment(self) -> List[dict]:
        """
        Extracts unique environmental descriptions from the data source.

        :return: A list of dictionaries containing unique environmental
            properties.
        """
        if not self.has_environment():
            return []

        descriptors = []
        properties = list(self.properties.keys())
        self.data = apply_code_mapping(self.data)
        results = self.data.get("results", [])
        for res_item in results:
            entry = {}
            for prop in properties:
                entry[prop] = res_item.get(prop)
            descriptors.append(dumps(entry))

        descriptors = set(descriptors)
        descriptors = [loads(d) for d in descriptors]

        # Convert properties into standardized format
        new_descriptors = []
        for descriptor in descriptors:
            new_descriptor = {
                "ecosystem": str(descriptor.get("ClassName", "")),
                "hydrologicClass": str(descriptor.get("Class_hydr", "")),
                "physioClimaticClass": str(descriptor.get("Class_phys", "")),
                "geomorphicClass": str(descriptor.get("Class_geom", "")),
            }
            new_descriptors.append(new_descriptor)
        return new_descriptors

    def has_environment(self, data=None) -> bool:
        """
        Determines whether the data source contains environmental information
        for the given geometry.

        :param data: Optional response data dictionary to evaluate.
        :return: ``True`` if environmental data is available, otherwise
            ``False``.
        """
        if data is None:
            data = self.data

        if data and data.get("properties"):
            values = data.get("properties", {}).get("Values", [])
            return len(values) > 0 and values != ["NoData"]
        return False


def apply_code_mapping(data: dict) -> dict:
    """
    Applies GloRiC classification code mappings to enrich unique reach types
    with standardized ecosystem and class descriptions.

    :param data: Raw response data dictionary containing ``properties.Values``
        or ``properties.reaches``.
    :return: Data dictionary enriched with a ``results`` list.
    """
    logger.debug("Applying GloRiC code mapping")
    mapping = get_gloric_code_mapping()
    reach_types_map = mapping.get("reachTypes", {})
    results = []

    if data and data.get("properties"):
        props = data["properties"]
        values = props.get("Values", [])
        if not values and props.get("reaches"):
            values = sorted(
                list(
                    {
                        str(r.get("Reach_type"))
                        for r in props["reaches"]
                        if r.get("Reach_type") is not None
                    }
                )
            )

        if values and values != ["NoData"]:
            for v in values:
                if v in ("NoData", None):
                    continue
                v_str = str(v)
                type_info = reach_types_map.get(v_str, {})
                results.append(
                    {
                        "Reach_type": v_str,
                        "ClassName": type_info.get(
                            "ClassName", f"River Reach Type {v_str}"
                        ),
                        "Class_hydr": type_info.get("reducedHydrologic", ""),
                        "Class_phys": type_info.get("reducedPhysioClimatic", ""),
                        "Class_geom": type_info.get("reducedGeomorphic", ""),
                    }
                )

    data["results"] = results
    return data


def get_gloric_code_mapping() -> dict:
    """
    Loads GloRiC attribute tables and class definitions from bundled JSON data.

    :return: Dictionary containing GloRiC attribute lookup mappings.
    """
    data_path = files("geoenv.data.data_source_attributes").joinpath(
        "gloric_attribute_table.json"
    )
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def download_dataset(
    cache_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Downloads the GloRiC v1.0 zipped shapefile from HydroSHEDS and extracts
    the shapefile bundle into the local cache directory.

    :param cache_dir: Target directory to cache the dataset.
    :return: Path to the extracted ``GloRiC_v10.shp`` file.
    """
    if cache_dir is None:
        base_cache = os.environ.get(
            "GEOENV_CACHE_DIR", str(Path.home() / ".cache" / "geoenv")
        )
        cache_dir = Path(base_cache) / "gloric_v1"
    else:
        cache_dir = Path(cache_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)
    target_shp = cache_dir / "GloRiC_v10_shapefile" / DEFAULT_SHP_NAME
    if target_shp.is_file():
        return target_shp

    direct_shp = cache_dir / DEFAULT_SHP_NAME
    if direct_shp.is_file():
        return direct_shp

    zip_path = cache_dir / "GloRiC_v10_shapefile.zip"
    if not (zip_path.is_file() and zipfile.is_zipfile(zip_path)):
        logger.info(
            f"Downloading GloRiC v1.0 dataset from {GLORIC_DOWNLOAD_URL} to {zip_path}..."
        )

        req = urllib.request.Request(
            GLORIC_DOWNLOAD_URL, headers={"User-Agent": "geoenv/0.5.0"}
        )
        with urllib.request.urlopen(req) as resp, open(zip_path, "wb") as out_file:
            total_bytes = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            while chunk := resp.read(4 * 1024 * 1024):
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_bytes > 0:
                    logger.debug(
                        f"Downloaded {downloaded / (1024 * 1024):.1f} MB of {total_bytes / (1024 * 1024):.1f} MB"
                    )

    logger.info(f"Extracting {zip_path} to {cache_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(cache_dir)

    if target_shp.is_file():
        return target_shp

    for p in cache_dir.rglob(DEFAULT_SHP_NAME):
        if p.is_file():
            return p

    raise FileNotFoundError(
        f"Downloaded GloRiC archive did not contain {DEFAULT_SHP_NAME}"
    )
