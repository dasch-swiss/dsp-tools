from __future__ import annotations

import json
from datetime import datetime

from loguru import logger

from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig


def write_id2iri_mapping(
    id2iri_mapping: dict[str, str],
    diagnostics: DiagnosticsConfig,
) -> None:
    """Writes the mapping of internal IDs to IRIs to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    servername = diagnostics.server_as_foldername
    id2iri_filename = f"{timestamp}_id2iri_mapping_{servername}.json"
    with open(id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"{datetime.now()}: The mapping of internal IDs to IRIs was written to {id2iri_filename}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
