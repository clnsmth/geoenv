"""
*environment.py*
"""

import daiquiri

logger = daiquiri.getLogger(__name__)


# pylint: disable=too-few-public-methods
class Environment:
    """
    The Environment class represents environmental descriptions retrieved from
    a ``DataSource``. It provides a structured way to store and manage
    environmental data.
    """

    def __init__(self, data: dict = None):
        """
        Initializes an Environment object with the given data.

        :param data: A dictionary containing environmental data.
        """
        self._data = data

    @property
    def data(self) -> dict:
        """
        Retrieves the stored environmental data.

        :return: A dictionary representing the environmental data.
        """
        return self._data

    @data.setter
    def data(self, data: dict):
        """
        Updates the environmental data.

        :param data: A dictionary containing updated environmental data.
        """
        self._data = data
