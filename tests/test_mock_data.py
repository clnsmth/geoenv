"""Test the mock_data"""

from json import loads, dumps
from importlib.resources import files
import pytest
from tests.data.create_mock_data import create_mock_response_content


def test_mock_response_content(use_mock, tmp_path):
    """Test the mock response content is consistent with real response data"""

    if use_mock:
        pytest.skip("Skipping test when use_mock is False")

    # Real response data
    create_mock_response_content(output_directory=tmp_path)

    # Compare against mocks
    # Iterate over files in the output directory
    for file in tmp_path.iterdir():
        # Open the file
        with open(file, "r", encoding="utf-8") as f:
            print(file.name)
            # Read the content
            content = f.read()
            # Read the corresponding mock file
            mock_file_path = files("tests.data.response").joinpath(file.name)
            with open(mock_file_path, "r", encoding="utf-8") as mock_file:
                # Read the mock content
                mock_content = mock_file.read()

                # Handle non-deterministic differences in the World Terrestrial
                # Ecosystems response originating from the "value" property
                # having the value "NoData" on occasion. This is a server-side
                # issue and not a problem with the code.
                if "wte_success" in file.name:
                    content = loads(content)
                    mock_content = loads(mock_content)
                    del content["value"]
                    del mock_content["value"]
                    content = dumps(content, indent=4)
                    mock_content = dumps(mock_content, indent=4)

                # Compare the content
                assert content == mock_content
