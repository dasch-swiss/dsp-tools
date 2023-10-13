from __future__ import annotations

import json
import os
from collections import namedtuple
from pathlib import Path
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xmlupload.upload_config import UploadConfig

MetricRecord = namedtuple("MetricRecord", ["res_id", "filetype", "filesize_mb", "event", "duration_ms", "mb_per_sec"])


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


def warn_failed_uploads(failed_uploads: list[str]) -> None:
    print(f"\nWARNING: Could not upload the following resources: {failed_uploads}\n")
    logger.warning(f"Could not upload the following resources: {failed_uploads}")


def write_metrics(
    metrics: list[MetricRecord],
    input_file: str | Path | etree._ElementTree[Any],
    config: UploadConfig,
) -> None:
    """Writes the metrics to a file."""
    match input_file:
        case str() | Path():
            metrics_filename = (
                f"{config.timestamp_str}_metrics_{config.server_as_foldername}_{Path(input_file).stem}.csv"
            )
        case _:
            metrics_filename = f"{config.timestamp_str}_metrics_{config.server_as_foldername}.csv"

    # write files and print info
    os.makedirs("metrics", exist_ok=True)
    df = pd.DataFrame(metrics)
    df.to_csv(f"metrics/{metrics_filename}")
    print(f"Total time of xmlupload: {sum(int(record.duration_ms) for record in metrics) / 1000:.1f} seconds")
