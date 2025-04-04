"""
*response.py*
"""

import importlib
import json
from typing import List, Union

import daiquiri
from yaml import safe_load
import pandas as pd
from geoenv.environment import Environment
from geoenv.geometry import Geometry

logger = daiquiri.getLogger(__name__)


class Response:
    """
    The Response class structures the results returned by the ``Resolver``
    into a standardized format. The response follows the GeoJSON format, with
    resolved environments and their descriptions stored in the ``properties``
    field.
    """

    def __init__(self, data: dict = None):
        """
        Initializes a Response object with optional data.

        :param data: A dictionary containing response data.
        """
        self._data = data
        self._properties = {
            "type": "Feature",
            "identifier": None,
            "geometry": None,
            "properties": {"description": None, "environment": []},
        }

    @property
    def data(self) -> dict:
        """
        Retrieves the response data.

        :return: The response data as a dictionary.
        """
        return self._data

    @data.setter
    def data(self, data: dict):
        """
        Updates the response data.

        :param data: A dictionary containing response data.
        """
        self._data = data

    @property
    def properties(self):
        """
        Retrieves the response properties, including metadata and environment
        details.

        :return: A dictionary containing response properties.
        """
        return self._properties

    @properties.setter
    def properties(self, properties: dict):
        """
        Updates the response properties.

        :param properties: A dictionary containing new response properties.
        """
        self._properties = properties

    def write(self, file_path: str) -> None:
        """
        Writes the response data to a file in JSON format.

        :param file_path: The file path where the response should be saved.
        """
        logger.debug(f"Writing response data to {file_path}")
        # pylint: disable=broad-exception-caught
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(json.dumps(self.data))
                logger.info(f"Successfully saved response data to {file_path}")
        except Exception as e:
            logger.error(
                f"Failed to write response data to {file_path}: {e}", exc_info=True
            )

    def read(self, file_path: str) -> "Response":
        """
        Reads response data from a JSON file and updates the object's data.

        :param file_path: The file path from which to read response data.
        :return: The updated Response object.
        """
        logger.debug(f"Attempting to read response data from {file_path}")
        # pylint: disable=broad-exception-caught
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.data = json.loads(file.read())
            logger.info(f"Successfully loaded response data from {file_path}")
        except Exception as e:
            logger.error(
                f"Failed to read response data from {file_path}: {e}", exc_info=True
            )
        return self

    # pylint: disable=too-many-locals
    def apply_term_mapping(self, semantic_resource: str = "ENVO") -> "Response":
        """
        Maps environmental terms in the response data to a specified semantic
        resource.

        :param semantic_resource: The semantic resource for mapping (default:
            "ENVO"). Options include: "ENVO".
        :return: The updated Response object with mapped terms.
        """
        logger.debug(
            f"Applying term mapping using {semantic_resource} in "
            f"{self.__class__.__name__}"
        )

        # Iterate over list of environments in data
        for environment in self.data["properties"]["environment"]:

            # Load SSSOM of environment for term mapping
            data_source = environment["dataSource"]["name"]
            sssom_file = importlib.resources.files("geoenv.data.sssom").joinpath(
                f"{data_source}-{semantic_resource.lower()}.sssom.tsv"
            )
            if not sssom_file.exists():
                logger.warning(
                    f"Mapping file {sssom_file} not found. Skipping term "
                    f"mapping for {data_source}."
                )
                return []
            sssom_meta_file = importlib.resources.files("geoenv.data.sssom").joinpath(
                f"{data_source}-{semantic_resource.lower()}.sssom.yml"
            )
            if not sssom_meta_file.exists():
                logger.warning(
                    f"Metadata file {sssom_meta_file} not found. Skipping term "
                    f"mapping for {data_source}."
                )
                return []
            with open(sssom_file, mode="r", encoding="utf-8") as f:
                sssom = pd.read_csv(f, sep="\t")
            with open(sssom_meta_file, mode="r", encoding="utf-8") as f:
                sssom_meta = safe_load(f)

            # Map each property value to semantic resource term, if possible
            envo_terms = []
            for _, value in environment["properties"].items():
                try:
                    label = sssom.loc[
                        sssom["subject_label"].str.lower() == value.lower(),
                        "object_label",
                    ].values[0]
                    curie = sssom.loc[
                        sssom["subject_label"].str.lower() == value.lower(), "object_id"
                    ].values[0]
                    curie_prefix = curie.split(":")[0]
                    uri = sssom_meta["curie_map"][curie_prefix] + curie.split(":")[1]
                    logger.debug(f"Mapped '{value}' to '{label}' ({uri})")
                except IndexError:
                    label = None
                    uri = None
                    logger.debug(f"No mapping found for '{value}' in {data_source}")

                # Don't add empty labels. Empty implies no mapping was found.
                if pd.notna(label) and uri is not None:
                    # Unmappable objects are useless. Don't add them.
                    if curie.lower() != "sssom:nomapping":
                        envo_terms.append({"label": label, "uri": uri})

            # Add list of semantic resource terms back to the environment
            # object
            environment["mappedProperties"] = envo_terms

        logger.info(
            f"Term mapping complete. Mapped terms added to "
            f"{self.__class__.__name__}."
        )
        return self

    def to_schema_org(self) -> dict:
        """
        Converts the response data to a Schema.org-compliant format.

        :return: A dictionary formatted according to Schema.org conventions.
        """
        logger.debug("Converting response data to Schema.org format")
        additional_property = [
            {
                "@type": "PropertyValue",
                "name": "Spatial reference system",
                "propertyID": "https://dbpedia.org/page/Spatial_reference_system",
                "value": "https://www.w3.org/2003/01/geo/wgs84_pos",
            }
        ]
        additional_property.extend(self._to_schema_org_additional_property())
        schema_org = {
            "@context": "https://schema.org/",
            "@id": self.data.get("identifier"),
            "@type": "Place",
            "description": self.data.get("properties").get("description"),
            "geo": self._to_schema_org_geo(),
            "additionalProperty": additional_property,
            "keywords": self._to_schema_org_keywords(),
        }
        logger.info("Successfully converted response data to Schema.org format")
        return schema_org

    def _to_schema_org_geo(self) -> Union[dict, None]:
        """
        Extracts and converts the geographic information to a
        Schema.org-compliant format.

        :return: A dictionary containing Schema.org-formatted geographic
            information.
        """
        if self.data["geometry"]["type"] == "Polygon":
            polygon = " ".join(
                [
                    f"{coord[1]} {coord[0]}"
                    for coord in self.data["geometry"]["coordinates"][0]
                ]
            )
            return {"@type": "GeoShape", "polygon": polygon}
        if self.data["geometry"]["type"] == "Point":
            x, y, *z = self.data["geometry"]["coordinates"]
            return {
                "@type": "GeoCoordinates",
                "latitude": y,
                "longitude": x,
                "elevation": z[0] if z else None,
            }
        return None

    def _to_schema_org_additional_property(self) -> List[dict]:
        """
        Converts response properties to Schema.org additional property format.

        :return: A list of dictionaries representing additional properties in
            Schema.org format.
        """
        environments = self.data["properties"]["environment"]
        if len(environments) == 0:
            return None

        # Flatten the list of environment properties into a single list
        additional_properties = []
        for environment in environments:
            for key, value in environment.get("properties").items():
                additional_properties.append(
                    {"@type": "PropertyValue", "name": key, "value": value}
                )

        # Remove duplicates
        additional_properties = list(
            {v["name"]: v for v in additional_properties}.values()
        )
        return additional_properties

    def _to_schema_org_keywords(self) -> List[dict]:
        """
        Extracts and formats keywords from the response for Schema.org
        compliance.

        :return: A list of dictionaries containing Schema.org keyword
            representations.
        """
        environments = self.data["properties"]["environment"]
        if len(environments) == 0:
            return None
        # Flatten the list of environment mappedProperties into a single list
        keywords = []
        for environment in environments:
            for term in environment.get("mappedProperties"):
                keywords.append(
                    {
                        "@id": term["uri"],
                        "@type": "DefinedTerm",
                        "name": term["label"],
                        "inDefinedTermSet": "https://ontobee.org/ontology/ENVO",
                        "termCode": term["uri"].split("/")[-1],
                    }
                )

        # Remove duplicates
        keywords = list({v["name"]: v for v in keywords}.values())
        return keywords


def construct_response(
    geometry: Geometry,
    environment: List[Environment],
    identifier: str = None,
    description: str = None,
) -> Response:
    """
    Compiles a response from the given geometry and environmental data.

    :param geometry: The spatial geometry for which environmental data is
        resolved.
    :param environment: A list of ``Environment`` objects describing the
        location.
    :param identifier: An optional identifier for tracking the response.
    :param description: An optional description associated with the response.
    :return: A ``Response`` object containing the constructed environmental
        data.
    """
    logger.debug("Starting response compilation")

    # Move data from Environment objects and into a list
    environments = []
    for env in environment:
        environments.append(env.data)

    result = {
        "type": "Feature",
        "identifier": identifier,
        "geometry": geometry.data,
        "properties": {"description": description, "environment": environments},
    }
    logger.debug(f"Compiled response with {len(environments)} environments")
    return Response(result)
