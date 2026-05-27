from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig


def write_id2iri_mapping(id2iri_mapping: dict[str, str], shortcode: str, diagnostics: DiagnosticsConfig) -> None:
    """Writes the mapping of internal IDs to IRIs to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    servername = diagnostics.server_as_foldername
    json_str = json.dumps(id2iri_mapping, ensure_ascii=False, indent=4)
    id2iri_filename_for_user = f"id2iri_{shortcode}_{servername}_{timestamp}.json"
    with open(id2iri_filename_for_user, "w", encoding="utf-8") as f:
        f.write(json_str)
        print(f"{datetime.now()}: The mapping of internal IDs to IRIs was written to {id2iri_filename_for_user}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename_for_user}")

    id_2_iri_folder = Path.home() / ".dsp-tools" / "id2iri"
    id_2_iri_folder.mkdir(parents=True, exist_ok=True)
    id2iri_filename_for_user_home = f"id2iri_{timestamp}_{shortcode}_{servername}.json"
    with open(id_2_iri_folder / id2iri_filename_for_user_home, "w", encoding="utf-8") as f:
        f.write(json_str)


def write_resources_as_jsonld(resources: list[dict[str, Any]], xml_file: Path | None) -> None:
    """Writes the serialised JSON-LD representations of all attempted resources to a file."""
    stem = xml_file.stem if xml_file is not None else "resources"
    filename = Path(f"{stem}.jsonld")
    content = json.dumps(resources, ensure_ascii=False, indent=4)
    filename.write_text(content, encoding="utf-8")
    print(f"{datetime.now()}: The serialised resources were written to {filename}")
    logger.info(f"The serialised resources were written to {filename}")
