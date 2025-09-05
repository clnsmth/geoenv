"""
*ecological_marine_units.py*
"""

import asyncio
from json import dumps, loads
from typing import List

import pandas as pd
import daiquiri
import aiohttp
from geoenv.data_sources.data_source import DataSource
from geoenv.geometry import Geometry
from geoenv.environment import Environment
from geoenv.utilities import user_agent
from geoenv.utilities import EnvironmentDataModel

logger = daiquiri.getLogger(__name__)


class EcologicalMarineUnits(DataSource):
    """
    A concrete implementation of ``DataSource`` that retrieves marine
    environmental classifications from the Ecological Marine Units dataset
    (Sayre 2023).


    **Note**
        - This data source supports the resolution of geometries with ``z``
          values (depth). To retrieve environmental data at different depths,
          include the ``z`` component in the input geometry. No additional
          property is required.
        - If no ``z`` value is specified in the geometry, all vertically
          stacked environments will be returned. If a ``z`` value is included,
          only the intersecting environment layers at that depth will be
          returned.

    **Further Information**
        - **Spatial Resolution**: Global coverage with a resolution of
          *1/4 degree*.
        - **Coverage**: Marine ecosystems worldwide, classified by *ocean name,
          depth, temperature, salinity, dissolved oxygen, nitrate, phosphate,
          and silicate*.
        - **Explore the Dataset**:
          `https://esri.maps.arcgis.com/home/item.html?
          id=58526e3af88b46a3a1d1eb1738230ee3
          <https://esri.maps.arcgis.com/home/item.html?id=
          58526e3af88b46a3a1d1eb1738230ee3>`_.

    **Citation**
        Sayre, R., 2023, Ecological Marine Units (EMUs): U.S. Geological
        Survey data release, `https://doi.org/10.5066/P9Q6ZSGN <https://doi.org/10.5066/P9Q6ZSGN>`_.
    """

    def __init__(self):
        """
        Initializes the EcologicalMarineUnits data source with default
        properties.
        """
        super().__init__()
        self._geometry = None
        self._data = None
        self._properties = {
            "OceanName": None,
            "Depth": None,
            "Temperature": None,
            "Salinity": None,
            "Dissolved Oxygen": None,
            "Nitrate": None,
            "Phosphate": None,
            "Silicate": None,
            "EMU_Descriptor": None,
        }

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

    # pylint: disable=duplicate-code
    async def get_environment(self, geometry: Geometry) -> List[Environment]:
        """
        Resolves a given geometry to environmental descriptions using the
        Ecological Marine Units dataset.

        :param geometry: The geographic location to resolve.
        :return: A list of ``Environment`` objects containing environmental
            classifications.
        """
        logger.debug(
            f"Starting environment resolution for geometry in "
            f"{self.__class__.__name__}"
        )

        self.geometry = geometry.data  # access z values to filter on depth

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
        Sends a request to the Ecological Marine Units data source and
        retrieves raw response data.

        :param session: An active aiohttp ClientSession.
        :param geometry: The geographic location to query.
        :return: A dictionary containing raw response data from the data
            source.
        """
        base = (
            "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/"
            + "EMU_2018"
            + "/FeatureServer/"
            + "0"
            + "/query"
        )
        payload = {
            "f": "json",
            "geometry": dumps(geometry.to_esri()["geometry"]),
            "geometryType": geometry.to_esri()["geometryType"],
            "where": "1=1",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "UnitTop,UnitBottom,OceanName,Name_2018",
            "distance": "10",
            "units": "esriSRUnit_NauticalMile",
            "multipatchOption": "xyFootprint",
            "outSR": '{"wkid":4326}',
            "returnIdsOnly": "false",
            "returnZ": "false",
            "returnM": "false",
            "returnExceededLimitFeatures": "true",
            "sqlFormat": "none",
            "orderByFields": "UnitTop desc",
            "returnDistinctValues": "false",
            "returnExtentOnly": "false",
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
        unique_emu_environments = self.unique_environment()
        for unique_emu_environment in unique_emu_environments:
            environment = EnvironmentDataModel()
            environment.set_identifier("https://doi.org/10.5066/P9Q6ZSGN")
            environment.set_data_source(self.__class__.__name__)
            environment.set_date_created()
            properties = self.set_properties(
                unique_environment_properties=unique_emu_environment
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
        data = self.convert_codes_to_values()
        descriptors = self.get_environments_for_geometry_z_values(data=data)
        return descriptors

    def has_environment(self) -> bool:
        res = len(self.data.get("features", []))
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

        # There are two properties returned by this data source (OceanName and
        # Name_2018), the latter of which is composed of 7 atomic properties.
        # Split Name_2018 into atomic properties and then zip the descriptors
        # and atomic property labels to create a dictionary of environment
        # properties.
        properties = loads(unique_environment_properties)["attributes"]
        ocean_name = properties.get("OceanName")
        descriptors = properties.get("Name_2018")
        descriptors = descriptors.split(",")
        descriptors = [g.strip() for g in descriptors]

        # Add ocean name to front of descriptors list in preparation for the
        # zipping operation below
        descriptors = [ocean_name] + descriptors
        properties = self.properties
        atomic_property_labels = properties.keys()
        environments = [dict(zip(atomic_property_labels, descriptors))]

        # Iterate over atomic properties and set labels
        environment = environments[0]
        for item in environment.keys():
            label = environment.get(item)
            properties[item] = label

        # Compose a readable EMU_Description classification by joining atomic
        # properties into a single string.
        emu_descriptor = list(properties.values())
        emu_descriptor = emu_descriptor[:-1]  # last one is the EMU_Descriptor
        # Handle edge case where some of the properties are None. This is an
        # issue with the data source.
        if None in emu_descriptor:
            emu_descriptor = ["n/a" if f is None else f for f in emu_descriptor]
        emu_descriptor = ", ".join(emu_descriptor)
        properties["EMU_Descriptor"] = emu_descriptor

        # Convert properties into a more readable format
        new_properties = {
            "oceanName": properties["OceanName"],
            "depth": properties["Depth"],
            "temperature": properties["Temperature"],
            "salinity": properties["Salinity"],
            "dissolvedOxygen": properties["Dissolved Oxygen"],
            "nitrate": properties["Nitrate"],
            "phosphate": properties["Phosphate"],
            "silicate": properties["Silicate"],
            "ecosystem": properties["EMU_Descriptor"],
        }
        return new_properties

    def convert_codes_to_values(self) -> dict:
        """
        Converts coded classification values (e.g., ``OceanName`` and other
        properties) into descriptive string values. This transformation ensures
        consistency between response objects across different datasets.

        :return: A dictionary with converted classification values.
        """
        data = self.data
        field_names = [field["name"] for field in data["fields"]]
        i = field_names.index("OceanName")
        ocean_name_map = pd.DataFrame(
            data.get("fields")[i].get("domain").get("codedValues")
        )

        # Create the code-value map for Name_2018
        i = field_names.index("Name_2018")
        name_2018_map = pd.DataFrame(
            data.get("fields")[i].get("domain").get("codedValues")
        )

        # Iterate over the features array replacing OceanName and
        # Name_2018 codes with corresponding values in the maps
        for i in range(len(data.get("features"))):
            # OceanName
            code = data.get("features")[i]["attributes"]["OceanName"]
            if code is None:
                value = "Not an ocean"
            else:
                value = ocean_name_map.loc[ocean_name_map["code"] == code, "name"].iloc[
                    0
                ]
            data.get("features")[i]["attributes"]["OceanName"] = value
            # Name_2018
            code = data.get("features")[i]["attributes"]["Name_2018"]

            # Not all locations have Name_2018 values (not sure why this is
            # the case).
            try:
                value = name_2018_map.loc[name_2018_map["code"] == code, "name"].iloc[0]
            except IndexError:
                value = "n/a"
            data.get("features")[i]["attributes"]["Name_2018"] = value
        return data

    def get_environments_for_geometry_z_values(self, data) -> List[dict]:
        """
        Extracts the depth (Z) values from the geometry property in the
        response object. This method is useful for analyzing environmental
        data at different depth levels.

        :param data: The response data containing geometry information.
        """
        # Get the z values from the geometry property of the response object
        geometry = self.geometry
        coordinates = geometry.get("coordinates")
        if len(coordinates) == 3:
            zmin = geometry.get("coordinates")[2]
            zmax = geometry.get("coordinates")[2]
        else:
            zmin = None
            zmax = None
        res = []
        if zmin is None or zmax is None:  # Case with no z values
            for item in data["features"]:
                parsed = {
                    "attributes": {
                        "OceanName": item["attributes"]["OceanName"],
                        "Name_2018": item["attributes"]["Name_2018"],
                    }
                }
                res.append(dumps(parsed))
        else:  # Case when z values are present
            for item in data["features"]:
                top = item["attributes"]["UnitTop"]
                bottom = item["attributes"]["UnitBottom"]
                # Case where zmin and zmax are equal
                if (top >= zmax >= bottom) and (top >= zmin >= bottom):
                    parsed = {
                        "attributes": {
                            "OceanName": item["attributes"]["OceanName"],
                            "Name_2018": item["attributes"]["Name_2018"],
                        }
                    }
                    res.append(dumps(parsed))
                # Case where zmin and zmax are not equal (a depth interval)
                if (top >= zmax >= bottom) or (top >= zmin >= bottom):
                    parsed = {
                        "attributes": {
                            "OceanName": item["attributes"]["OceanName"],
                            "Name_2018": item["attributes"]["Name_2018"],
                        }
                    }
                    res.append(dumps(parsed))

        # Get the unique set of environments (don't want duplicates) and
        # convert back to a list as preferred by subsequent operations
        res = set(res)
        res = list(res)
        return res
