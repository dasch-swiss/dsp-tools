from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lxml import etree

from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def write_id2iri_mapping(
    id2iri_mapping: dict[str, str],
    input_file: str | Path | etree._ElementTree[Any],
    timestamp_str: str,
) -> None:
    """Writes the mapping of internal IDs to IRIs to a file."""
    match input_file:
        case str() | Path():
            id2iri_filename = f"{Path(input_file).stem}_id2iri_mapping_{timestamp_str}.json"
        case _:
            id2iri_filename = f"{timestamp_str}_id2iri_mapping.json"
    with open(id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
