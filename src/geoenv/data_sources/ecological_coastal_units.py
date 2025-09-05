"""
*ecological_coastal_units.py*
"""

import asyncio
from json import dumps
from typing import List

import daiquiri
import aiohttp
from geoenv.data_sources.data_source import DataSource
from geoenv.geometry import Geometry
from geoenv.environment import Environment
from geoenv.utilities import user_agent
from geoenv.utilities import EnvironmentDataModel, get_properties

logger = daiquiri.getLogger(__name__)


class EcologicalCoastalUnits(DataSource):
    """
    A concrete implementation of ``DataSource`` that retrieves coastal
    environmental classifications from the Ecological Coastal Units dataset
    (Sayre 2023).

    **Note**
        - Note, this data source does not accept ``Point`` geometries directly.
          Because coastal units are represented as vector polygons, input
          geometries must overlap with them for successful resolution. However,
          ``Point`` geometries can be processed by setting the ``buffer``
          property, which converts them into circular polygons of a given
          radius (in kilometers). These polygons are then resolved against the
          dataset, and all overlapping coastal units are returned in the
          response.

    **Further Information**
        - **Spatial Resolution**: Global coverage with a resolution of
          *1 km (or shorter)*.
        - **Coverage**: Costal ecosystems worldwide, classified by *sinuosity,
          erodibility, temperature and moisture regime, river discharge,
          wave height, tidal range, marine physical environment, turbidity,
          and chlorophyll*.
        - **Explore the Dataset**:
          `https://www.arcgis.com/home/item.html?id=
          54df078334954c5ea6d5e1c34eda2c87 <https://www.arcgis.com/home/
          item.html?id=54df078334954c5ea6d5e1c34eda2c87>`_.

    **Citation**
        Sayre, R., 2023, Global Ecological Classification of Coastal Segment
        Units: U.S. Geological Survey data release,
        `https://doi.org/10.5066/P9HWHSPU <https://doi.org/10.5066/P9HWHSPU>`_.
    """

    def __init__(self, buffer: float = None):
        """
        Initializes the EcologicalCoastalUnits data source with default
        properties.
        """
        super().__init__()
        self._geometry = None
        self._data = None
        self._properties = {
            "Slope": None,
            "Sinuosity": None,
            "Erodibility": None,
            "Temperature and Moisture Regime": None,
            "River Discharge": None,
            "Wave Height": None,
            "Tidal Range": None,
            "Marine Physical Environment": None,
            "Turbidity": None,
            "Chlorophyll": None,
            "CSU_Descriptor": None,
        }
        self._buffer = buffer

    @property
    # pylint: disable=duplicate-code
    def geometry(self) -> dict:
        return self._geometry

    @geometry.setter
    # pylint: disable=duplicate-code
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
    def buffer(self) -> float:
        """
        Retrieves the buffer distance used for spatial resolution.

        Since this data source does not accept ``Point`` geometries directly,
        setting the ``buffer`` parameter converts them into circular polygons
        of a given radius (in kilometers) before resolution. All overlapping
        coastal units within the buffered area will be included in the
        response.

        :return: The buffer radius as a float. Units are in **kilometers**.
        """
        return self._buffer

    @buffer.setter
    def buffer(self, buffer: float):
        """
        Sets the buffer distance used for spatial resolution.

        :param buffer: The buffer distance in **kilometers** as a float.
        """
        self._buffer = buffer

    # pylint: disable=duplicate-code
    async def get_environment(self, geometry: Geometry) -> List[Environment]:
        """
        Resolves a given geometry to environmental descriptions using the
        Ecological Coastal Units dataset.

        :param geometry: The geographic location to resolve.
        :return: A list of ``Environment`` objects containing environmental
            classifications.
        """
        logger.debug(
            f"Starting environment resolution for geometry in "
            f"{self.__class__.__name__}"
        )

        # Enable buffer-based sampling for points. Without this, the data
        # source would return None because environments are represented as
        # line vectors, meaning point locations would not overlap with any
        # features.
        if geometry.geometry_type() == "Point" and self.buffer is not None:
            logger.debug(
                f"Applying buffer of {self.buffer} kilometers to point " f"geometry"
            )
            geometry.data = geometry.point_to_polygon(buffer=self.buffer)

        # This method remains `async` and uses `aiohttp` by design, even though
        # it only resolves a single geometry at a time. This is critical to
        # ensure the method is non-blocking and integrates safely into a larger
        # asyncio application. Using a synchronous library like `requests` here
        # would freeze the entire event loop, halting all other concurrent tasks
        # until this single network request completes.
        async with aiohttp.ClientSession() as session:
            self.data = await self._request(session, geometry)

        environments = self.convert_data()
        logger.info(
            f"Resolved {len(environments)} environments for geometry in "
            f"{self.__class__.__name__}"
        )
        return environments

    async def _request(
        self, session: aiohttp.ClientSession, geometry: Geometry
    ) -> dict:
        """
        Sends a request to the Ecological Coastal Units data source and
        retrieves raw response data.

        :param session: An active aiohttp ClientSession.
        :param geometry: The geographic location to query.
        :return: A dictionary containing raw response data from the data
            source.
        """
        base = (
            "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/"
            "services/Ecological_Coastal_Units__ECU__1km_Segments/"
            "FeatureServer/0/query"
        )
        payload = {
            "f": "geojson",
            "geometry": dumps(geometry.to_esri()["geometry"]),
            "geometryType": geometry.to_esri()["geometryType"],
            "where": "1=1",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnTrueCurves": "false",
            "returnIdsOnly": "false",
            "returnCountOnly": "false",
            "returnZ": "false",
            "returnM": "false",
            "returnExtentOnly": "false",
            "returnGeometry": "false",
        }

        logger.debug(f"Sending request to {self.__class__.__name__}")

        # pylint: disable=unused-variable
        # pylint: disable=duplicate-code
        try:
            async with session.get(
                base, params=payload, timeout=10, headers=user_agent()
            ) as response:
                response.raise_for_status()
                logger.debug(
                    f"Received response from {self.__class__.__name__}. "
                    f"Status: {response.status}"
                )
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(
                f"Failed to fetch data from {self.__class__.__name__}. " f"Error: {e}",
                exc_info=True,
            )
            return {}

    # pylint: disable=duplicate-code
    def convert_data(self) -> List[Environment]:
        logger.debug(f"Starting data conversion in {self.__class__.__name__}")
        result = []
        unique_ecu_environments = self.unique_environment()
        for unique_ecu_environment in unique_ecu_environments:
            environment = EnvironmentDataModel()
            environment.set_identifier("https://doi.org/10.5066/P9HWHSPU")
            environment.set_data_source(self.__class__.__name__)
            environment.set_date_created()
            properties = self.set_properties(
                unique_environment_properties=unique_ecu_environment
            )
            environment.set_properties(properties)
            result.append(Environment(data=environment.data))
            logger.debug(f"Converted environment: {properties}")
        logger.debug(
            f"Successfully converted {len(result)} environments in "
            f"{self.__class__.__name__}"
        )
        return result

    def unique_environment(self) -> List[dict]:
        if not self.has_environment():
            return []
        prop = "CSU_Descriptor"
        descriptors = get_properties(self._data, [prop])[prop]
        descriptors = set(descriptors)
        descriptors = list(descriptors)
        return descriptors

    def has_environment(self) -> bool:
        res = len(self._data.get("features", []))
        if res == 0:
            return False
        return True

    def set_properties(self, unique_environment_properties) -> dict:
        """
        Sets the properties for the data source based on unique environmental
        descriptions.

        :param unique_environment_properties: A dictionary containing
            environmental classification attributes.
        :return: The updated properties dictionary.
        """
        if len(unique_environment_properties) == 0:
            return {}

        # There is only one property returned by this data source
        # (CSU_Descriptor), which is composed of 10 atomic properties. Split
        # the CSU_Descriptor into atomic properties and then zip the
        # descriptors and atomic property labels to create a dictionary of
        # environment properties.
        descriptors = unique_environment_properties
        descriptors = descriptors.split(",")
        descriptors = [g.strip() for g in descriptors]
        atomic_property_labels = self._properties.keys()
        environments = [dict(zip(atomic_property_labels, descriptors))]

        # Iterate over atomic properties and set labels
        environment = environments[0]
        properties = self._properties
        for item in environment.keys():
            label = environment.get(item)
            properties[item] = label

        # Compose a readable CSU_Descriptor class by joining atomic properties
        # into a single string.
        csu_descriptor = list(properties.values())
        csu_descriptor = csu_descriptor[:-1]  # last one is the CSU_Description
        csu_descriptor = ", ".join(csu_descriptor)
        properties["CSU_Descriptor"] = csu_descriptor

        # Convert property labels into a more readable format
        new_properties = {
            "slope": properties["Slope"],
            "sinuosity": properties["Sinuosity"],
            "erodibility": properties["Erodibility"],
            "temperatureAndMoistureRegime": properties[
                "Temperature and Moisture Regime"
            ],
            "riverDischarge": properties["River Discharge"],
            "waveHeight": properties["Wave Height"],
            "tidalRange": properties["Tidal Range"],
            "marinePhysicalEnvironment": properties["Marine Physical Environment"],
            "turbidity": properties["Turbidity"],
            "chlorophyll": properties["Chlorophyll"],
            "ecosystem": properties["CSU_Descriptor"],
        }
        return new_properties
