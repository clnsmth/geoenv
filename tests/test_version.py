"""Test the package versioning utility"""

from unittest.mock import patch
from importlib.metadata import PackageNotFoundError
import geoenv


def test_get_version():
    """Test that get_version returns a valid version string"""
    version = geoenv.get_version()
    assert isinstance(version, str)
    assert len(version) > 0
    assert version == geoenv.__version__


def test_get_version_not_installed():
    """Test that get_version returns 'unknown' when package is not installed"""
    with patch("geoenv.version", side_effect=PackageNotFoundError):
        version = geoenv.get_version()
        assert version == "unknown"
