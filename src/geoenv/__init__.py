"""geoenv"""

from importlib.metadata import version, PackageNotFoundError


def get_version() -> str:
    """
    Returns the current semantic version of the geoenv package.
    """
    try:
        return version("geoenv")
    except PackageNotFoundError:
        return "unknown"


__version__ = get_version()

__all__ = ["get_version"]
