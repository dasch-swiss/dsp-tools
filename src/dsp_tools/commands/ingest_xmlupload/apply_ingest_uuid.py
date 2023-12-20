from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import cast

import pandas as pd
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def get_mapping_dict_from_file(shortcode: str) -> dict[str, str]:
    """
    This functions returns the information to replace the original filepaths with the identifier from dsp-ingest.

    Args:
        shortcode: Shortcode of the project

    Returns:
        dictionary with original: identifier from dsp-ingest

    Raises:
        InputError: if no file was found
    """
    filepath = Path(f"mapping-{shortcode}.csv")
    if filepath.exists():
        df = pd.read_csv(filepath)
        msg = f"The file '{filepath}' is used to map the internal SIPI image IDs to the original filepaths."
        print(msg)
        logger.info(msg)
        return dict(zip(df["original"].tolist(), df["derivative"].tolist()))
    else:
        raise InputError(f"No mapping CSV file was found in the current working directory {Path.cwd()}")


def replace_filepath_with_sipi_uuid(
    xml_tree: etree._ElementTree[etree._Element],
    orig_path_2_uuid_filename: dict[str, str],
) -> tuple[etree._ElementTree[etree._Element], IngestInformation]:
    """
    Replace the original filepaths in the <bitstream> tags by the uuid filenames of the uploaded files.

    Args:
        xml_tree: The parsed original XML tree
        orig_path_2_uuid_filename: Mapping from original filenames to uuid filenames from the mapping.csv

    Returns:
        The XML tree with the replaced filepaths (modified in place)
        Message informing if all referenced files were uploaded or not.
    """
    no_uuid_found = []
    used_media_paths = []
    new_tree = deepcopy(xml_tree)
    for elem in new_tree.iter():
        if etree.QName(elem).localname.endswith("bitstream"):
            if (img_path := elem.text) in orig_path_2_uuid_filename:
                elem.text = orig_path_2_uuid_filename[img_path]
                used_media_paths.append(img_path)
            else:
                no_uuid_found.append((cast("etree._Element", elem.getparent()).attrib.get("id"), elem.text))
    unused_media_paths = [x for x in orig_path_2_uuid_filename if x not in used_media_paths]
    return new_tree, IngestInformation(unused_media_paths=unused_media_paths, media_no_uuid=no_uuid_found)
