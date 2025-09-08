"""Create mock data for the tests"""

import asyncio
from json import dumps
from pathlib import Path
from importlib.resources import files

import aiohttp

from geoenv.geometry import Geometry
from geoenv.data_sources import WorldTerrestrialEcosystems
from geoenv.data_sources import EcologicalCoastalUnits
from geoenv.data_sources import EcologicalMarineUnits
from geoenv.resolver import construct_response
from tests.conftest import load_geometry


async def create_mock_response_content(
    output_directory: Path = files("tests.data.response"),
) -> None:
    """Get response content for each data_source, and for both success and fail
    scenarios, then write to file in tests/data. Success scenarios are when the
    input geometry returns results. Fail scenarios are when the input geometry
    returns no results.
    """

    # Create a single session to be reused for all requests
    async with aiohttp.ClientSession() as session:

        # WTE Success
        geometry = Geometry(load_geometry("point_on_land"))
        data_source = WorldTerrestrialEcosystems()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("wte_success.json"), "w") as f:
            f.write(json)

        # WTE Fail
        geometry = Geometry(load_geometry("point_on_ocean"))
        data_source = WorldTerrestrialEcosystems()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("wte_fail.json"), "w") as f:
            f.write(json)

        # ECU Success
        geometry = Geometry(load_geometry("polygon_on_land_and_ocean"))
        data_source = EcologicalCoastalUnits()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("ecu_success.json"), "w") as f:
            f.write(json)

        # ECU Fail
        geometry = Geometry(load_geometry("polygon_on_land"))
        data_source = EcologicalCoastalUnits()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("ecu_fail.json"), "w") as f:
            f.write(json)

        # EMU Success
        geometry = Geometry(load_geometry("polygon_on_ocean"))
        data_source = EcologicalMarineUnits()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("emu_success.json"), "w") as f:
            f.write(json)

        # EMU Fail
        geometry = Geometry(load_geometry("polygon_on_land"))
        data_source = EcologicalMarineUnits()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(output_directory.joinpath("emu_fail.json"), "w") as f:
            f.write(json)

        # EMU Success (another one, for testing depth inputs)
        geometry = Geometry(load_geometry("point_on_ocean_with_depth"))
        data_source = EcologicalMarineUnits()
        response = await data_source._request(session, geometry)
        json = dumps(response, indent=4)
        with open(
            output_directory.joinpath("emu_success_point_on_ocean_with_depth.json"), "w"
        ) as f:
            f.write(json)


def create_schema_org_fixture(
    output_directory: Path = files("tests.data.schema_org"),
) -> None:
    # This code should match that of the data_model fixture for purposes of
    # comparison.

    data_source = WorldTerrestrialEcosystems()
    geometry = Geometry(load_geometry("point_on_land"))
    environment = data_source.get_environment(geometry)
    data = construct_response(
        geometry,
        environment,
        identifier="5b4edec5-ea5e-471a-8a3c-2c1171d59dee",
        description="Point on land",
    )

    data.apply_term_mapping()
    schema_org = dumps(data.to_schema_org(), indent=4)

    with open(output_directory.joinpath("schema_org.jsonld"), "w") as f:
        f.write(schema_org)


if __name__ == "__main__":
    asyncio.run(create_mock_response_content())
    # create_schema_org_fixture()
