"""
*data_source.py*
"""

from abc import ABC, abstractmethod
from typing import List
from geoenv.geometry import Geometry
from geoenv.environment import Environment


class DataSource(ABC):
    """
    Abstract base class for data sources that provide environmental information
    based on geographic queries. Implementing classes must define methods for
    resolving spatial geometries to environmental descriptions.
    """

    def __init__(self):
        """
        Initializes the DataSource with placeholders for geometry, data, and
        properties.
        """
        self._geometry = None
        self._data = None
        self._properties = None

    @property
    @abstractmethod
    def geometry(self) -> dict:
        """
        Retrieves the geometry associated with the data source.

        :return: A dictionary representing the geometry.
        """

    @geometry.setter
    @abstractmethod
    def geometry(self, geometry: dict):
        """
        Sets the geometry for querying the data source.

        :param geometry: A dictionary representing the geometry.
        """

    @property
    @abstractmethod
    def data(self) -> dict:
        """
        Retrieves the data returned by the data source.

        :return: A dictionary containing retrieved environmental data.
        """

    @data.setter
    @abstractmethod
    def data(self, data: dict):
        """
        Sets the environmental data for the data source.

        :param data: A dictionary containing environmental data.
        """

    @property
    @abstractmethod
    def properties(self) -> dict:
        """
        Retrieves the properties associated with the data source.

        :return: A dictionary containing metadata and additional properties.
        """

    @properties.setter
    @abstractmethod
    def properties(self, properties: dict):
        """
        Sets the properties for the data source.

        :param properties: A dictionary containing metadata and additional
            properties.
        """

    @abstractmethod
    async def get_environment(self, geometry: Geometry) -> List[Environment]:
        """
        Resolves a given geometry to environmental descriptions using the data
        source.

        :param geometry: The geographic location to get_environment.
        :return: A list of Environment containing environmental descriptions.
        """

    @abstractmethod
    def convert_data(self) -> List[Environment]:
        """
        Converts raw data from the data source into a standardized format.

        :return: A list of Environment representing converted environmental
            data.
        """

    @abstractmethod
    def unique_environment(self) -> List[dict]:
        """
        Extracts unique environmental descriptions from the data source.

        :return: A list of dictionaries containing unique environmental
            descriptions.
        """

    @abstractmethod
    def has_environment(self) -> bool:
        """
        Determines whether the data source contains environmental information
        for the given geometry.

        :return: ``True`` if environmental data is available, otherwise
            ``False``.
        """
