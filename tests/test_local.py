# Importing necessary modules and packages
from typing import Any

import pytest

# Speckle is a data platform for AEC; here we're importing essential modules from it
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport


# Setting up some pytest fixtures for testing
# Fixtures are a way to provide consistent test data or configuration for each test


@pytest.fixture()
def speckle_token(request) -> str:
    """Get the Speckle token from test configuration.
    These variables may be in a `.env` file or as secrets in your CI/CD pipeline."""
    return request.config.SPECKLE_TOKEN


@pytest.fixture()
def speckle_server_url(request) -> str:
    """Provide a speckle server URL for the test suite.
    Defaults to localhost if not specified. Useful only if you are spinning up a local server.
    """
    return request.config.SPECKLE_SERVER_URL


@pytest.fixture()
def test_version_object(speckle_server_url: str, speckle_token: str) -> Base:
    """Retrieve a specific commit from the Speckle server."""
    test_client = SpeckleClient(speckle_server_url, True)
    test_client.authenticate_with_token(speckle_token)

    # Sample project/stream and version/commit IDs
    # Could also be environment variables
    project_id = "PROJECT_ID"  # Replace with your stream ID
    version_id = "VERSION_ID"  # Replace with your commit ID

    transport = ServerTransport(client=test_client, stream_id=project_id)
    version = test_client.commit.get(project_id, version_id)
    version_object = version.referencedObject
    obj = operations.receive(obj_id=version_object, remote_transport=transport)

    return obj


# Main test functions
def test_real_data(test_version_object: Any, speckle_server_url: str):
    """
    Test your code against a real Speckle commit.
    """

    assert isinstance(Base, test_version_object)

    pass
