from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
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
    severity: ValidationSeverity
    ignore_duplicate_files_warning: bool
    is_on_prod_server: bool


@dataclass  # noqa: RUF049  An enum class should not be decorated with `@dataclass`  # Fix this later
class ValidationSeverity(Enum):
    ERROR = 3
    WARNING = 2
    INFO = 1
