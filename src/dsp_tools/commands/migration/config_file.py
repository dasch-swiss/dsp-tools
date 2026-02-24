from pathlib import Path

from dsp_tools.commands.migration.models import MigrationInfo


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
    pass
