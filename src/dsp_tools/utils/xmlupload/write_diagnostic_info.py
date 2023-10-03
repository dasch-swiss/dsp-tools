from __future__ import annotations

import json
import os
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import regex
from lxml import etree

from dsp_tools.utils.create_logger import get_logger

MetricRecord = namedtuple("MetricRecord", ["res_id", "filetype", "filesize_mb", "event", "duration_ms", "mb_per_sec"])


logger = get_logger(__name__)


def _transform_server_url_to_foldername(server: str) -> str:
    """
    Take the server URL and transform it so that it can be used as foldername.

    Args:
        server: server, e.g. "https://api.test.dasch.swiss/" or "http://0.0.0.0:3333"

    Returns:
        simplified version, e.g. "test.dasch.swiss" or "localhost"
    """
    server_substitutions = {
        r"https?://": "",
        r"^api\.": "",
        r":\d{2,5}/?$": "",
        r"/$": "",
        r"0.0.0.0": "localhost",
    }
    for pattern, repl in server_substitutions.items():
        server = regex.sub(pattern, repl, server)
    return server


def determine_save_location_of_diagnostic_info(
    server: str,
    proj_shortcode: str,
    onto_name: str,
) -> tuple[Path, str, str]:
    """
    Determine the save location for diagnostic info that will be used if the xmlupload is interrupted.
    They are going to be stored in ~/.dsp-tools/xmluploads/server/shortcode/ontoname.
    This path is computed and created.

    Args:
        server: URL of the DSP server where the data is uploaded to
        proj_shortcode: 4-digit hexadecimal shortcode of the project
        onto_name: name of the ontology that the data belongs to

    Returns:
        a tuple consisting of the absolute full path to the storage location,
        a version of the server URL that can be used as foldername,
        and the timestamp string that can be used as component of file names
        (so that different diagnostic files of the same xmlupload have the same timestamp)
    """
    server_as_foldername = _transform_server_url_to_foldername(server)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    save_location = Path.home() / Path(".dsp-tools") / "xmluploads" / server_as_foldername / proj_shortcode / onto_name
    save_location.mkdir(parents=True, exist_ok=True)
    return save_location, server_as_foldername, timestamp_str


def write_id2iri_mapping_and_metrics(
    id2iri_mapping: dict[str, str],
    metrics: Optional[list[MetricRecord]],
    failed_uploads: list[str],
    input_file: Union[str, Path, etree._ElementTree[Any]],
    timestamp_str: str,
    server_as_foldername: str,
) -> bool:
    """
    Writes the id2iri mapping and the metrics into the current working directory,
    and prints the failed uploads (if applicable).

    Args:
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (initially empty, gets filled during the upload)
        metrics: list with the metric records collected until now (gets filled during the upload)
        failed_uploads: ids of resources that could not be uploaded (initially empty, gets filled during the upload)
        input_file: path to the XML file or parsed ElementTree
        timestamp_str: timestamp for the name of the log files
        server_as_foldername: simplified version of the server URL that can be used as folder name

    Returns:
        True if there are no failed_uploads, False otherwise
    """
    # determine names of files
    if isinstance(input_file, (str, Path)):
        id2iri_filename = f"{Path(input_file).stem}_id2iri_mapping_{timestamp_str}.json"
        metrics_filename = f"{timestamp_str}_metrics_{server_as_foldername}_{Path(input_file).stem}.csv"
    else:
        id2iri_filename = f"{timestamp_str}_id2iri_mapping.json"
        metrics_filename = f"{timestamp_str}_metrics_{server_as_foldername}.csv"

    # write files and print info
    success = True
    with open(id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
    if failed_uploads:
        print(f"\nWARNING: Could not upload the following resources: {failed_uploads}\n")
        logger.warning(f"Could not upload the following resources: {failed_uploads}")
        success = False
    if metrics:
        os.makedirs("metrics", exist_ok=True)
        df = pd.DataFrame(metrics)
        df.to_csv(f"metrics/{metrics_filename}")
        print(f"Total time of xmlupload: {sum(int(record.duration_ms) for record in metrics) / 1000:.1f} seconds")

    return success
