from __future__ import annotations

import json

from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def write_id2iri_mapping(
    id2iri_mapping: dict[str, str],
    input_file_name: str | None,
    timestamp_str: str,
) -> None:
    """Writes the mapping of internal IDs to IRIs to a file."""
    if input_file_name:
        id2iri_filename = f"{input_file_name}_id2iri_mapping_{timestamp_str}.json"
    else:
        id2iri_filename = f"id2iri_mapping_{timestamp_str}.json"
    with open(id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
