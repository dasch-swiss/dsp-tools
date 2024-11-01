from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import cast

import pandas as pd
from loguru import logger
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.create_resources.user_information import IngestInformation
from dsp_tools.models.exceptions import InputError


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
    if not filepath.is_file():
        raise InputError(f"No mapping CSV file was found at {filepath}.")
    df = pd.read_csv(filepath)
    msg = f"The file '{filepath}' is used to map the internal original filepaths to the internal image IDs."
    print(msg)
    logger.info(msg)
    return dict(zip(df["original"].tolist(), df["derivative"].tolist()))


def replace_filepath_with_internal_filename(
    xml_tree: etree._Element,
    orig_path_2_asset_id: dict[str, str],
) -> tuple[etree._Element, IngestInformation]:
    """
    Replace the original filepaths in the `<bitstream>` tags by the id filenames of the uploaded files.

    Args:
        xml_tree: The parsed original XML tree
        orig_path_2_asset_id: Mapping from original filenames to asset IDs from the mapping.csv

    Returns:
        A copy of the XMl tree, with the replaced filepaths.
        Message informing if all referenced files were uploaded or not.
    """
    no_id_found = []
    used_media_file_paths = []
    new_tree = deepcopy(xml_tree)
    for elem in new_tree.iter():
        if not etree.QName(elem).localname.endswith("bitstream") or not elem.text:
            continue
        img_path_str = elem.text
        if img_path_str not in orig_path_2_asset_id:
            img_path_str = "/" + img_path_str
        if img_path_str in orig_path_2_asset_id:
            elem.text = orig_path_2_asset_id[img_path_str]
            used_media_file_paths.append(img_path_str)
        else:
            no_id_found.append((cast("etree._Element", elem.getparent()).attrib["id"], str(elem.text)))

    unused_media_paths = [x for x in orig_path_2_asset_id if x not in used_media_file_paths]
    return new_tree, IngestInformation(unused_mediafiles=unused_media_paths, mediafiles_no_id=no_id_found)
