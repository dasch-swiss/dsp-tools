from dataclasses import dataclass
from pathlib import Path


@dataclass
class MigrationConfig:
    shortcode: str
    export_savepath: Path
    reference_savepath: Path
    keep_local_export: bool


@dataclass
class ServerInfo:
    server: str
    user: str
    password: str


@dataclass
class MigrationInfo:
    config: MigrationConfig
    source: ServerInfo | None
    target: ServerInfo | None
