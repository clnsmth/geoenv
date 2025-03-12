"""For testing the geoenv module."""

from src.geoenv.geoenv import hello_world


def test_test():
    """Test test"""
    assert 1 == 1


def test_hello_world():
    """Test hello_world"""
    assert hello_world("Hello world", False) == "Hello world"
