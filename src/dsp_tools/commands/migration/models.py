from dataclasses import dataclass
from pathlib import Path

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ImportId


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


@dataclass
class ReferenceInfo:
    export_id: ExportId | None
    import_id: ImportId | None
    project_iri: str
