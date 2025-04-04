"""Test the environment module."""

from geoenv.environment import Environment


def test_environment_init():
    """Test Environment class initialization has the expected attributes."""
    environment = Environment()
    assert environment.data is None


def test_data():
    """Test the data attribute of the Environment class."""
    geometry = Environment({"type": "Environment"})
    # Get
    assert geometry.data is not None
    # Set
    default_value = geometry.data
    geometry.data = {"type": "Different Environment"}
    assert geometry.data != default_value
