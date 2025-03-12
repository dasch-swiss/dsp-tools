import itertools
import socket
from dataclasses import dataclass

from test.e2e.setup_testcontainers.artifacts import E2E_TESTDATA

TESTCONTAINER_PORTS_LOCKFILES = E2E_TESTDATA / "testcontainer_port_lockfiles"
TESTCONTAINER_PORTS_LOCKFILES.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class ExternalContainerPorts:
    fuseki: int
    sipi: int
    ingest: int
    api: int


def get_ports() -> ExternalContainerPorts:
    num_of_ports_needed = 4
    port_window: list[int] = []
    for port in itertools.count(1025):
        if len(port_window) == num_of_ports_needed:
            break
        if _reserve_port(port):
            port_window.append(port)

    return ExternalContainerPorts(*port_window)


def _reserve_port(port: int) -> bool:
    with socket.socket() as s:
        if s.connect_ex(("localhost", port)) == 0:
            return False
    try:
        (TESTCONTAINER_PORTS_LOCKFILES / str(port)).touch(exist_ok=False)
    except FileExistsError:
        return False
    return True


def release_ports(ports: ExternalContainerPorts) -> None:
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.fuseki)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.sipi)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.ingest)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.api)).unlink()
