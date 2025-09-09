"""
*resolver.py*

The primary client-facing API for resolving spatial geometries to environmental
descriptions.
"""

import asyncio
from typing import List
import daiquiri
from geoenv.data_sources.data_source import DataSource
from geoenv.geometry import Geometry
from geoenv.response import construct_response, Response

logger = daiquiri.getLogger(__name__)


class Resolver:
    """
    The Resolver class serves as the primary client-facing API for querying
    environmental data. Clients configure an instance with one or more
    ``DataSource`` objects and use the ``resolve`` method to retrieve
    environment descriptions based on geographic locations.

    The results are mapped to a specified semantic resource (default: ENVO)
    and returned in a structured ``Response`` object.
    """

    def __init__(self, data_source: List[DataSource]):
        """
        Initializes the Resolver with a list of ``DataSource`` instances.

        :param data_source: A list of ``DataSource`` objects that provide
            environmental data.
        """
        self._data_source = data_source

    @property
    def data_source(self) -> List[DataSource]:
        """
        Retrieves the list of configured ``DataSource`` instances.

        :return: The list of data sources.
        """
        return self._data_source

    @data_source.setter
    def data_source(self, data_source: List[DataSource]):
        """
        Updates the list of ``DataSource`` instances used by the resolver.

        :param data_source: A new list of data sources.
        """
        self._data_source = data_source

    async def resolve(
        self,
        geometry: Geometry,
        semantic_resource: str = "ENVO",
        identifier: str = None,
        description: str = None,
    ) -> Response:
        """
        Resolves a given ``Geometry`` to one or more environments using the
        configured data sources. The results are mapped to a semantic resource
        (e.g., ENVO) and returned as a ``Response`` object.

        :param geometry: The spatial geometry to resolve.
        :param semantic_resource: The semantic resource to use for mapping
            (default: "ENVO").
        :param identifier: An optional identifier for tracking the resolution
            request.
        :param description: An optional description to annotate the resolution
            request.
        :return: A ``Response`` object containing the resolved environmental
            data.
        """
        logger.info(
            f"Resolving geometry with identifier: '{identifier}' and "
            f"description: '{description}'"
        )
        # pylint: disable=broad-exception-caught
        try:
            tasks = [item.get_environment(geometry) for item in self.data_source]
            results_nested = await asyncio.gather(*tasks)
            results = []
            for environment in results_nested:
                results.extend(environment)
            result = construct_response(
                geometry=geometry,
                environment=results,
                identifier=identifier,
                description=description,
            )
            result.apply_term_mapping(semantic_resource)
            logger.info("Resolution complete for geometry")
            return result
        except Exception as e:
            logger.error(f"Failed to resolve geometry: {e}", exc_info=True)
            result = construct_response(geometry=geometry, environment=[])
            return result


# if __name__ == "__main__":
#
#     import time
#     from json import dumps
#     from geoenv.data_sources import (WorldTerrestrialEcosystems,
#                                      EcologicalMarineUnits,
#                                      EcologicalCoastalUnits)
#     from geoenv.resolver import Resolver
#     from geoenv.geometry import Geometry
#
#     start_time = time.time()
#
#     # Create a geometry in GeoJSON format
#     point_on_land = {"type": "Point", "coordinates": [-122.622364, 37.905931]}
#     geometry = Geometry(point_on_land)
#
#     # Configure the resolver with one or more data sources
#     resolver = Resolver(
#         data_source=[
#             WorldTerrestrialEcosystems(),
#             EcologicalMarineUnits(),
#             EcologicalCoastalUnits(),
#         ]
#     )
#
#     # Resolve the geometry to environmental descriptions
#     response = asyncio.run(
#         resolver.resolve(
#             geometry,
#             identifier="5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
#             description="Point on land",
#         )
#     )
#
#     duration = time.time() - start_time
#     print(f"requests took {duration:.2f} seconds")
#
#     # The response is a GeoJSON feature with environmental properties
#     print(dumps(response.data, indent=2))
#
#     # Format as Schema.org
#     schema_org = response.to_schema_org()
