from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.lists_only import create_lists_only
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def _create_lists_only(creds: ServerCredentials) -> None:
    assert create_lists_only(Path("testdata/json-project/create-project-0003.json"), creds)


# TODO: request some of the lists and see if they were correct
