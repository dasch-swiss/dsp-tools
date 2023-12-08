from __future__ import annotations

import glob
from typing import cast

import pandas as pd
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.user_information import IngestInformation
from dsp_tools.models.exceptions import InputError


def get_mapping_dict_from_file() -> dict[str, str]:
    """
    This functions returns the information to replace the original filepaths with the identifier from dsp-ingest.

    Returns:
        dictionary with original: identifier from dsp-ingest

    Raises:
        InputError: if no file was found
    """
    if filepath := glob.glob("mapping-*.csv"):
        df = pd.read_csv(filepath[0])
        print(f"The file '{filepath[0]}' is used to map the internal SIPI image IDs to the original filepaths.")
        return dict(zip(df["original"].tolist(), df["derivative"].tolist()))
    else:
        raise InputError("No mapping csv file was found in the directory.")


def replace_filepath_with_sipi_uuid(
    xml_tree: etree._ElementTree[etree._Element],
    orig_path_2_uuid_filename: dict[str, str],
) -> tuple[etree._ElementTree[etree._Element], IngestInformation]:
    """
    Replace the original filepaths in the <bitstream> gags by the uuid filenames of the uploaded files.

    Args:
        xml_tree: The parsed original XML tree
        orig_path_2_uuid_filename: Mapping from original filenames to uuid filenames from the mapping.csv

    Returns:
        The XML tree with the replaced filepaths (modified in place)
        Message informing if all referenced files were uploaded or not.
    """
    no_uuid_found = []
    used_media_paths = []
    for elem in xml_tree.iter():
        if etree.QName(elem).localname.endswith("bitstream"):
            if (img_path := elem.text) in orig_path_2_uuid_filename:
                elem.text = orig_path_2_uuid_filename[img_path]
                used_media_paths.append(img_path)
            else:
                no_uuid_found.append((cast("etree._Element", elem.getparent()).attrib.get("id"), elem.text))
    unused_media_paths = [x for x in orig_path_2_uuid_filename if x not in used_media_paths]
    return xml_tree, IngestInformation(unused_media_paths=unused_media_paths, media_no_uuid=no_uuid_found)
