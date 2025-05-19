from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ServerCredentials:
    """Contains credentials to connect to a server."""

    user: str
    password: str
    server: str
    dsp_ingest_url: str = "http://0.0.0.0:3340"


@dataclass(frozen=True)
class ValidateDataConfig:
    """Contains the configuration for validate data."""

    xml_file: Path
    save_graph_dir: Path | None
