"""
*global_lakes_and_wetlands.py*
"""

import hashlib
import os
import shutil
import urllib.request
import zipfile
from json import dumps, loads
from pathlib import Path
from typing import List, Optional, Tuple, Union
from importlib.resources import files

import daiquiri
import numpy as np
import rasterio
import rasterio.mask

from geoenv.data_sources.data_source import DataSource
from geoenv.geometry import Geometry
from geoenv.environment import Environment
from geoenv.utilities import EnvironmentDataModel

logger = daiquiri.getLogger(__name__)

FIGSHARE_ARTICLE_ID = 28519994
FIGSHARE_FILES_API = f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE_ID}/files"
FALLBACK_DOWNLOAD_URL = "https://ndownloader.figshare.com/files/54001814"
FALLBACK_MD5 = "aea80ff46211b349ffbaa871442fd0ed"
DEFAULT_DATASET_NAME = "GLWD_v2_0_main_class.tif"


class GlobalLakesAndWetlands(DataSource):
    """
    A concrete implementation of ``DataSource`` that retrieves lake and wetland
    ecosystem classifications from the Global Lakes and Wetlands Database
    (GLWD) version 2.0 (Lehner et al. 2025).

    **Note**
        - This data source operates on a high-resolution local GeoTIFF raster
          (15 arc-second / ~500 m global resolution) representing 33 distinct
          lake, river, and wetland classes.
        - ``Point`` geometries are resolved directly by querying the pixel
          value at the specified coordinates.
        - ``Polygon`` geometries are resolved directly via raster masking
          (``rasterio.mask``), extracting all lake and wetland classes
          intersecting the polygon boundary with 100% pixel coverage.

    **Further Information**
        - **Spatial Resolution**: Global coverage at *15 arc-seconds* (~500 m
          at equator).
        - **Coverage**: Worldwide inland waters and wetlands classified into
          33 types incorporating hydrology, vegetation, salinity, and origin.
        - **Dataset Information**:
          `https://www.hydrosheds.org/products/glwd
          <https://www.hydrosheds.org/products/glwd>`_.

    **Citation**
        Lehner, B., Anand, M., Fluet-Chouinard, E., Tan, F., Aires, F., Allen,
        G.H., et al. (2025). Mapping the world’s inland surface waters: an
        upgrade to the Global Lakes and Wetlands Database (GLWD v2). Earth
        System Science Data. `https://doi.org/10.6084/m9.figshare.28519994
        <https://doi.org/10.6084/m9.figshare.28519994>`_.
    """

    def __init__(
        self,
        data_path: Optional[Union[str, Path]] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        grid_size: Optional[float] = None,
        auto_download: bool = True,
    ):
        """
        Initializes the GlobalLakesAndWetlands data source.

        :param data_path: Optional direct path to the GLWD GeoTIFF file (e.g.
            ``GLWD_v2_0_main_class.tif``). If not provided, the default cache
            directory will be checked.
        :param cache_dir: Optional directory to store cached datasets. Defaults
            to ``~/.cache/geoenv/glwd_v2`` or the ``GEOENV_CACHE_DIR``
            environment variable.
        :param grid_size: Optional grid size parameter retained for DataSource
            interface compatibility.
        :param auto_download: If True, automatically downloads the dataset if
            not found locally.
        """
        super().__init__()
        self._geometry = None
        self._data = None
        self._properties = {
            "ClassID": None,
            "ClassName": None,
        }
        self._grid_size = grid_size
        self._auto_download = auto_download

        if cache_dir is not None:
            self._cache_dir = Path(cache_dir)
        else:
            base_cache = os.environ.get(
                "GEOENV_CACHE_DIR", str(Path.home() / ".cache" / "geoenv")
            )
            self._cache_dir = Path(base_cache) / "glwd_v2"

        if data_path is not None:
            self._data_path = Path(data_path)
        else:
            env_path = os.environ.get("GEOENV_GLWD_DATA_PATH")
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
    def grid_size(self) -> Optional[float]:
        """
        Retrieves the grid size used for spatial resolution.

        :return: The grid size as a float or None.
        """
        return self._grid_size

    @grid_size.setter
    def grid_size(self, grid_size: Optional[float]):
        """
        Sets the grid size used for spatial resolution.

        :param grid_size: A float representing grid size in degrees or None.
        """
        if grid_size is not None and not isinstance(grid_size, (int, float)):
            raise TypeError("grid_size must be a float or int")
        if grid_size is not None and grid_size <= 0:
            raise ValueError("grid_size must be greater than 0")
        self._grid_size = float(grid_size) if grid_size is not None else None

    @property
    def data_path(self) -> Optional[Path]:
        """
        Returns the path to the GLWD raster dataset.
        """
        return self._data_path

    @property
    def cache_dir(self) -> Path:
        """
        Returns the cache directory used for storing GLWD data.
        """
        return self._cache_dir

    def ensure_dataset(self) -> Path:
        """
        Ensures that the GLWD raster dataset is available locally. If the dataset
        is not found and ``auto_download`` is True, downloads and caches the
        dataset from Figshare.

        :return: Path to the local GeoTIFF file.
        :raises FileNotFoundError: If dataset is missing and auto_download is False.
        """
        if self._data_path is not None and self._data_path.is_file():
            return self._data_path

        # Check default cache paths
        candidates = [
            self._cache_dir / DEFAULT_DATASET_NAME,
            self._cache_dir / "GLWD_v2_0_combined_classes" / DEFAULT_DATASET_NAME,
        ]
        for candidate in candidates:
            if candidate.is_file():
                self._data_path = candidate
                return self._data_path

        # Check recursive search in cache_dir
        if self._cache_dir.is_dir():
            for candidate in self._cache_dir.rglob(DEFAULT_DATASET_NAME):
                if candidate.is_file():
                    self._data_path = candidate
                    return self._data_path

        # Check if an existing zip archive is in cache_dir and can be extracted
        zip_path = self._cache_dir / "GLWD_v2_0_combined_classes_tif.zip"
        if zip_path.is_file() and zipfile.is_zipfile(zip_path):
            logger.info(f"Found existing GLWD archive at {zip_path}. Extracting...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self._cache_dir)

            for candidate in self._cache_dir.rglob(DEFAULT_DATASET_NAME):
                if candidate.is_file():
                    self._data_path = candidate
                    return self._data_path

        if not self._auto_download:
            raise FileNotFoundError(
                f"GLWD dataset '{DEFAULT_DATASET_NAME}' not found at "
                f"{self._data_path or self._cache_dir}. Set auto_download=True "
                f"or download manually."
            )

        downloaded_path = download_dataset(cache_dir=self._cache_dir)
        self._data_path = downloaded_path
        return self._data_path

    async def get_environment(self, geometry: Geometry) -> List[Environment]:
        """
        Resolves the given ``Geometry`` to lake and wetland classifications.

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
        Samples the local GLWD raster for the given point or polygon geometry.

        :param session: Unused session parameter for DataSource interface parity.
        :param geometry: The Geometry object or GeoJSON dict to sample.
        :return: Dictionary structured as ``{"properties": {"Values": [...]}}``.
        """
        nodata_response = {"properties": {"Values": ["NoData"]}}
        try:
            raster_file = self.ensure_dataset()
        except FileNotFoundError as e:
            logger.warning(f"Could not load GLWD dataset: {e}")
            return nodata_response

        geom_data, geom_type = self._parse_geometry(geometry)
        if geom_type == "Point":
            return self._sample_point(raster_file, geom_data)
        if geom_type == "Polygon":
            return self._mask_polygon(raster_file, geom_data)

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
    def _sample_point(raster_file: Path, geom_data: dict) -> dict:
        """Samples a single point from the GLWD raster."""
        coords = geom_data.get("coordinates", [])
        if len(coords) < 2:
            return {"properties": {"Values": ["NoData"]}}
        x, y = coords[0], coords[1]
        try:
            with rasterio.open(raster_file) as src:
                sampled = list(src.sample([(x, y)]))
                if sampled and len(sampled[0]) > 0:
                    val = int(sampled[0][0])
                    if val > 0 and val not in (src.nodata, 255):
                        return {"properties": {"Values": [str(val)]}}
        except Exception as e:
            logger.error(
                f"Failed to query GLWD raster at ({x}, {y}): {e}",
                exc_info=True,
            )
        return {"properties": {"Values": ["NoData"]}}

    @staticmethod
    def _mask_polygon(raster_file: Path, geom_data: dict) -> dict:
        """Extracts unique GLWD classes inside a polygon via rasterio.mask."""
        try:
            with rasterio.open(raster_file) as src:
                out_image, _ = rasterio.mask.mask(
                    src, [geom_data], crop=True, nodata=src.nodata
                )
                unique_vals = np.unique(out_image)
                valid_vals = [
                    str(int(v))
                    for v in unique_vals
                    if v > 0 and v not in (src.nodata, 255)
                ]
                if valid_vals:
                    return {"properties": {"Values": valid_vals}}
        except ValueError:
            logger.debug("Polygon geometry does not overlap GLWD raster")
        except Exception as e:
            logger.error(
                f"Failed to mask GLWD raster for polygon: {e}",
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
        unique_glwd_environments = self.unique_environment()
        for unique_glwd_environment in unique_glwd_environments:
            environment = EnvironmentDataModel()
            environment.set_identifier("https://doi.org/10.6084/m9.figshare.28519994")
            environment.set_data_source(self.__class__.__name__)
            environment.set_date_created()
            environment.set_properties(unique_glwd_environment)
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
        properties = self.properties.keys()
        self.data = apply_code_mapping(self.data)
        results = self.data.get("results", [])
        for result in results:
            res = {}
            for item in properties:
                res[item] = result.get(item)
            res = dumps(res)
            descriptors.append(res)
        descriptors = set(descriptors)
        descriptors = [loads(d) for d in descriptors]

        # Convert properties into standardized format
        new_descriptors = []
        for descriptor in descriptors:
            new_descriptor = {
                "classId": str(descriptor.get("ClassID", "")),
                "ecosystem": descriptor.get("ClassName", ""),
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
            values = data["properties"].get("Values")
            if values:
                for val in values:
                    if val is not None and str(val) not in {"NoData", "0", "00"}:
                        return True
        return False


def apply_code_mapping(json_data: dict) -> dict:
    """
    Maps GLWD numeric classification codes to structured descriptions using
    the pre-generated raster attribute table.

    :param json_data: Raw response dictionary containing numeric classification
        codes in ``json_data["properties"]["Values"]``.
    :return: A dictionary containing mapped environmental results.
    """
    mapping_file = files("geoenv.data.data_source_attributes").joinpath(
        "glwd_attribute_table.json"
    )
    with mapping_file.open("r", encoding="utf-8") as f:
        attribute_table = loads(f.read())

    mapped_results = []
    values = json_data.get("properties", {}).get("Values", [])
    for code in values:
        if code in ("NoData", None, "0", "00", 0):
            continue
        code_str = str(code)
        if code_str in attribute_table:
            entry = attribute_table[code_str]
            mapped_results.append(
                {
                    "ClassID": entry["ClassID"],
                    "ClassName": entry["ClassName"],
                }
            )
    return {"results": mapped_results}


def fetch_figshare_metadata(
    api_url: str = FIGSHARE_FILES_API,
) -> Tuple[str, Optional[str]]:
    """
    Queries Figshare REST API for the GLWD dataset files metadata to find
    the download URL and MD5 checksum for GLWD_v2_0_combined_classes_tif.zip.

    :param api_url: The Figshare articles files API endpoint.
    :return: Tuple of (download_url, computed_md5).
    """
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "geoenv"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            files_data = loads(resp.read().decode("utf-8"))
            for item in files_data:
                if (
                    item.get("id") == 54001814
                    or item.get("name") == "GLWD_v2_0_combined_classes_tif.zip"
                ):
                    return (
                        item.get("download_url", FALLBACK_DOWNLOAD_URL),
                        item.get("computed_md5", FALLBACK_MD5),
                    )
    except Exception as e:
        logger.warning(
            f"Could not fetch Figshare API metadata: {e}. Using fallback URL."
        )

    return FALLBACK_DOWNLOAD_URL, FALLBACK_MD5


def download_dataset(
    cache_dir: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Downloads the GLWD v2.0 combined classes GeoTIFF archive from Figshare and
    extracts the main classification raster into the local cache directory.

    :param cache_dir: Target directory to cache the dataset.
    :return: Path to the extracted ``GLWD_v2_0_main_class.tif`` file.
    """
    if cache_dir is None:
        base_cache = os.environ.get(
            "GEOENV_CACHE_DIR", str(Path.home() / ".cache" / "geoenv")
        )
        cache_dir = Path(base_cache) / "glwd_v2"
    else:
        cache_dir = Path(cache_dir)

    cache_dir.mkdir(parents=True, exist_ok=True)
    target_tif = cache_dir / DEFAULT_DATASET_NAME

    if target_tif.is_file():
        return target_tif

    zip_path = cache_dir / "GLWD_v2_0_combined_classes_tif.zip"
    if not (zip_path.is_file() and zipfile.is_zipfile(zip_path)):
        url, expected_md5 = fetch_figshare_metadata()
        logger.info(f"Downloading GLWD v2.0 dataset from {url} to {zip_path}...")

        req = urllib.request.Request(url, headers={"User-Agent": "geoenv"})
        hasher = hashlib.md5()
        with urllib.request.urlopen(req) as resp, open(zip_path, "wb") as out_file:
            while chunk := resp.read(1024 * 1024):
                hasher.update(chunk)
                out_file.write(chunk)

        computed_md5 = hasher.hexdigest()
        if expected_md5 and computed_md5 != expected_md5:
            logger.warning(
                f"MD5 checksum mismatch for {zip_path}: computed {computed_md5}, expected {expected_md5}"
            )
        else:
            logger.info(f"MD5 checksum verified successfully: {computed_md5}")

    logger.info(f"Extracting {zip_path} to {cache_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(cache_dir)

    # Check extracted locations
    if target_tif.is_file():
        return target_tif

    nested_tif = cache_dir / "GLWD_v2_0_combined_classes" / DEFAULT_DATASET_NAME
    if nested_tif.is_file():
        return nested_tif

    # Search recursively for GLWD_v2_0_main_class.tif
    for p in cache_dir.rglob(DEFAULT_DATASET_NAME):
        return p

    raise FileNotFoundError(
        f"Could not find {DEFAULT_DATASET_NAME} after extracting {zip_path}."
    )
