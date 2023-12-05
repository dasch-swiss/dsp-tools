import glob
from typing import cast

import pandas as pd
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.user_messages import IngestMessage


def get_mapping_dict_from_file() -> dict[str, str]:
    """
    This functions returns the information to replace the original filepaths with the identifier from dsp-ingest.

    Returns:
        dictionary with original: identifier from dsp-ingest
    """
    filepath = glob.glob("mapping-*.csv")[0]
    df = pd.read_csv(filepath)
    return dict(zip(df["original"].tolist(), df["derivative"].tolist()))


def replace_bitstream_paths(
    xml_tree: "etree._ElementTree[etree._Element]",
    orig_path_2_uuid_filename: dict[str, str],
) -> tuple["etree._ElementTree[etree._Element]", IngestMessage]:
    """
    Replace the original filepaths in the <bitstream> gags by the uuid filenames of the processed files.

    Args:
        xml_tree: The parsed original XML tree
        orig_path_2_uuid_filename: Mapping from original filenames to uuid filenames (from the pickle file)

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
    unused_media_paths = [x for x in orig_path_2_uuid_filename.keys() if x not in used_media_paths]
    return xml_tree, IngestMessage(unused_media_paths=unused_media_paths, media_no_uuid=no_uuid_found)
