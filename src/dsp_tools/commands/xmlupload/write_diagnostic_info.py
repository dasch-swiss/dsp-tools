from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from loguru import logger

from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig


def write_id2iri_mapping(
    id2iri_mapping: dict[str, str], shortcode: str, diagnostics: DiagnosticsConfig, is_on_prod_like_server: bool
) -> None:
    """Writes the mapping of internal IDs to IRIs to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    servername = diagnostics.server_as_foldername
    id2iri_filename = f"id2iri_{shortcode}_{servername}_{timestamp}.json"
    id_2_iri_folder = Path.home() / ".dsp-tools" / "id2iri"
    id_2_iri_folder.mkdir(parents=True, exist_ok=True)
    with open(id_2_iri_folder / id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
    if is_on_prod_like_server:
        with open(id2iri_filename, "x", encoding="utf-8") as f:
            json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
            print(f"{datetime.now()}: The mapping of internal IDs to IRIs was written to {id2iri_filename}")
            logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
