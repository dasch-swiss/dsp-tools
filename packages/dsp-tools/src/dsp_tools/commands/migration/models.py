from dataclasses import dataclass
from pathlib import Path

from dsp_vre_lib.clients import ExportId
from dsp_vre_lib.clients import ImportId


@dataclass
class MigrationConfig:
    shortcode: str
    export_savepath: Path
    reference_savepath: Path
    keep_local_export: bool
    skip_assets: bool


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
