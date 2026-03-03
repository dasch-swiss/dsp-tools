import json
import re
from pathlib import Path
from typing import Any

import yaml

from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.commands.migration.exceptions import InvalidMigrationConfigFile
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ReferenceInfo
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.utils.json_parsing import parse_json_file

_DEFAULT_EXPORT_SAVEPATH = Path("~/.dsp-tools/migration/")


def create_migration_config(shortcode: str, cwd: Path) -> bool:
    """Write a template migration YAML config to cwd/migration-{shortcode}.yaml."""
    output_path = cwd / f"migration-{shortcode}.yaml"
    if output_path.exists():
        print(f"WARNING: '{output_path}' already exists. Aborting to avoid overwriting it.")
        return False
    template = f"""---
shortcode: "{shortcode}"
source-server:
  - server:
  - user:
  - password:
target-server:
  - server:
  - user:
  - password:
keep-local-export: false  # If set to true, you must manually remove the zip. Please note, that they may be very large.
export-savepath: {_DEFAULT_EXPORT_SAVEPATH}  # We recommend to keep the default path.
"""
    output_path.write_text(template, encoding="utf-8")
    print(f"Migration config written to '{output_path}'.")
    return True


def parse_config_file(filepath: Path) -> MigrationInfo:
    data = _parse_yaml(filepath)
    config = _parse_config_info(data, filepath)
    source = _parse_server_info(data.get("source-server"), "source-server", filepath)
    target = _parse_server_info(data.get("target-server"), "target-server", filepath)
    return MigrationInfo(config=config, source=source, target=target)


def _parse_yaml(filepath: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise InvalidMigrationConfigFile(f"Failed to parse YAML file '{filepath}': {e}") from e
    if not isinstance(data, dict):
        raise InvalidMigrationConfigFile(
            f"The migration config file '{filepath}' does not contain a valid YAML mapping."
        )
    return data


def _parse_config_info(data: dict[str, Any], filepath: Path) -> MigrationConfig:
    shortcode = data.get("shortcode")
    if not shortcode:
        raise InvalidMigrationConfigFile(
            f"The migration config file '{filepath}' is missing the required 'shortcode' field."
        )
    shortcode_str = str(shortcode)
    if not re.fullmatch(r"[0-9A-Fa-f]{4}", shortcode_str):
        raise InvalidMigrationConfigFile(
            f"The 'shortcode' in '{filepath}' must be a 4-character hexadecimal string (e.g. '0806'). "
            f"Got: '{shortcode_str}'. "
            f"Make sure the shortcode is quoted in the YAML file."
        )
    savepath_raw = data.get("export-savepath")
    export_base_path = Path(savepath_raw).expanduser() if savepath_raw else _DEFAULT_EXPORT_SAVEPATH.expanduser()
    export_savepath = export_base_path / f"export-{shortcode_str}.zip"
    reference_savepath = export_base_path / f"migration-references-{shortcode_str}.json"
    keep_local_export = bool(data.get("keep-local-export", False))
    config = MigrationConfig(
        shortcode=shortcode_str,
        export_savepath=export_savepath,
        reference_savepath=reference_savepath,
        keep_local_export=keep_local_export,
    )
    return config


def _parse_server_info(
    items: list[dict[str, Any]] | None,
    section_name: str,
    filepath: Path,
) -> ServerInfo | None:
    if not items:
        return None
    merged: dict[str, Any] = {}
    for item in items:
        merged.update(item)
    server = merged.get("server")
    user = merged.get("user")
    password = merged.get("password")
    if server is None and user is None and password is None:
        return None
    missing = [name for name, val in [("server", server), ("user", user), ("password", password)] if val is None]
    if missing:
        raise InvalidMigrationConfigFile(
            f"The '{section_name}' section in '{filepath}' is incomplete. Missing fields: {', '.join(missing)}."
        )
    return ServerInfo(server=str(server), user=str(user), password=str(password))


def write_or_update_reference_json(
    json_path: Path,
    *,
    export_id: ExportId | None = None,
    import_id: ImportId | None = None,
    project_iri: str | None = None,
) -> None:
    if json_path.exists():
        reference_info = parse_json_file(json_path)
    else:
        reference_info = {}
    if export_id:
        reference_info["export_id"] = export_id.id_
    if import_id:
        reference_info["import_id"] = import_id.id_
    if project_iri:
        reference_info["project_iri"] = project_iri
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reference_info, f, indent=4, ensure_ascii=False)


def parse_reference_json(json_path: Path) -> ReferenceInfo:
    parsed_file = parse_json_file(json_path)
    export_id, import_id = parsed_file.get("export_id"), parsed_file.get("import_id")
    return ReferenceInfo(
        export_id=ExportId(export_id) if export_id else None,
        import_id=ImportId(import_id) if import_id else None,
        project_iri=parsed_file["project_iri"],
    )
