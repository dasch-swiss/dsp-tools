from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.utils import get_canonical_server_and_dsp_ingest_url
from dsp_tools.commands.mapping.exceptions import InvalidMappingConfigFileError
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import MappingInfo

TEMPLATE = """---
shortcode: "{shortcode}"
ontology: "{ontology}"
excel-file: 
user: 
password: 
server: 
"""


def create_mapping_config(shortcode: str, ontology: str, mapping_path: Path) -> bool:
    """Write a template mapping YAML config to cwd/mapping-{shortcode}-{ontology}.yaml."""
    mapping_path.write_text(TEMPLATE.format(shortcode=shortcode, ontology=ontology), encoding="utf-8")
    print(f"Mapping config written to '{mapping_path}'.")
    print("Please fill in the blank fields: excel-file, server, user, password.")
    return True


def parse_mapping_config(filepath: Path) -> MappingInfo:
    data = _parse_yaml(filepath)
    config = MappingConfig(
        shortcode=_require_field(data, "shortcode", filepath),
        ontology=_require_field(data, "ontology", filepath),
        excel_file=Path(_require_field(data, "excel-file", filepath)),
    )
    parsed_server = _require_field(data, "server", filepath)
    resolved_server, _ = get_canonical_server_and_dsp_ingest_url(parsed_server)
    server = ServerCredentials(
        user=_require_field(data, "user", filepath),
        password=_require_field(data, "password", filepath),
        server=resolved_server,
    )
    return MappingInfo(config=config, server=server)


def _parse_yaml(filepath: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(filepath.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        logger.error(e)
        raise InvalidMappingConfigFileError(f"Failed to parse YAML file '{filepath}'") from None
    if not isinstance(data, dict):
        raise InvalidMappingConfigFileError(
            f"The mapping config file '{filepath}' does not contain a valid YAML mapping."
        )
    return data


def _require_field(data: dict[str, Any], field: str, filepath: Path) -> str:
    value = data.get(field)
    if not value:
        raise InvalidMappingConfigFileError(
            f"The mapping config file '{filepath}' is missing the required '{field}' field."
        )
    return str(value)
