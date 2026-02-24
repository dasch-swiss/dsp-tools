from pathlib import Path
from typing import Any

import yaml

from dsp_tools.commands.migration.exceptions import InvalidMigrationConfigFile
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo

_DEFAULT_EXPORT_SAVEPATH = Path("~/.dsp-tools/migration/")


def create_migration_config(shortcode: str, cwd: Path) -> bool:
    """Write a template migration YAML config to cwd/migration-{shortcode}.yaml."""
    output_path = cwd / f"migration-{shortcode}.yaml"
    if output_path.exists():
        print(f"WARNING: '{output_path}' already exists. Aborting to avoid overwriting it.")
        return False
    template = f"""---
shortcode: {shortcode}
source-server:
  - server:
  - user:
  - password:
target-server:
  - server:
  - user:
  - password:
keep-local-export: false  # If set to true, you must manually remove the zip. Please note that they may be very large.
export-savepath: ~/.dsp-tools/migration/  # We recommend to keep the default path.
---
"""
    output_path.write_text(template, encoding="utf-8")
    print(f"Migration config written to '{output_path}'.")
    return True


def parse_config_file(filepath: Path) -> MigrationInfo:
    try:
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise InvalidMigrationConfigFile(f"Failed to parse YAML file '{filepath}': {e}") from e
    if not isinstance(data, dict):
        raise InvalidMigrationConfigFile(
            f"The migration config file '{filepath}' does not contain a valid YAML mapping."
        )
    shortcode = data.get("shortcode")
    if not shortcode:
        raise InvalidMigrationConfigFile(
            f"The migration config file '{filepath}' is missing the required 'shortcode' field."
        )
    savepath_raw = data.get("export-savepath")
    export_savepath = Path(savepath_raw).expanduser() if savepath_raw else _DEFAULT_EXPORT_SAVEPATH.expanduser()
    keep_local_export = bool(data.get("keep-local-export", False))
    config = MigrationConfig(
        shortcode=str(shortcode),
        export_savepath=export_savepath,
        keep_local_export=keep_local_export,
    )
    source = _parse_server_info(data.get("source-server"), "source-server", filepath)
    target = _parse_server_info(data.get("target-server"), "target-server", filepath)
    return MigrationInfo(config=config, source=source, target=target)


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
