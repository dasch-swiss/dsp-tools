import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional, cast

from lxml import etree

from dsp_tools.commands.fast_xmlupload.upload_files import get_pkl_files
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def _get_paths_from_pkl_files(pkl_files: list[Path]) -> dict[str, str]:
    """
    Read the pickle file(s) returned by the processing step.

    Args:
        pkl_files: pickle file(s) returned by the processing step

    Raises:
        UserError: If for a file, no derivative was found

    Returns:
        dict of original paths to uuid filenames
    """
    orig_path_2_processed_path: list[tuple[Path, Optional[Path]]] = []
    for pkl_file in pkl_files:
        orig_path_2_processed_path.extend(pickle.loads(pkl_file.read_bytes()))

    orig_path_2_uuid_filename: dict[str, str] = {}
    for orig_path, processed_path in orig_path_2_processed_path:
        if processed_path:
            orig_path_2_uuid_filename[str(orig_path)] = str(processed_path.name)
        else:
            raise UserError(
                f"There is no processed file for {orig_path}. The fast xmlupload cannot be started, "
                "because the resource that uses this file would fail."
            )

    return orig_path_2_uuid_filename


def replace_bitstream_paths(
    xml_tree: "etree._ElementTree[etree._Element]",
    orig_path_2_uuid_filename: dict[str, str],
) -> "etree._ElementTree[etree._Element]":
    """
    Replace the original filepaths in the <bitstream> gags by the uuid filenames of the processed files.

    Args:
        xml_tree: The parsed original XML tree
        orig_path_2_uuid_filename: Mapping from original filenames to uuid filenames (from the pickle file)

    Raises:
        UserError: If for a file, no derivative was found

    Returns:
        The XML tree with the replaced filepaths (modified in place)
    """
    for elem in xml_tree.iter():
        if etree.QName(elem).localname.endswith("bitstream"):
            if elem.text in orig_path_2_uuid_filename:
                elem.text = orig_path_2_uuid_filename[elem.text]
            else:
                res_id = cast("etree._Element", elem.getparent()).attrib.get("id")
                raise UserError(
                    f"Resource {res_id}: Cannot find processed derivatives for {elem.text}. "
                    "The fast xmlupload cannot be started, because the resource that uses this file would fail."
                )
    return xml_tree


def fast_xmlupload(
    xml_file: str,
    user: str,
    password: str,
    dsp_url: str,
    sipi_url: str,
) -> bool:
    """
    This function reads an XML file
    and imports the data described in it onto the DSP server,
    using the fast XML upload method.
    Before using this method,
    the original files must be processed by the processing step,
    and uploaded by the upoad step.

    Args:
        xml_file: path to XML file containing the resources
        e.g. Path('multimedia/nested/subfolder/test.tif'), Path('tmp/0b/22/0b22570d-515f-4c3d-a6af-e42b458e7b2b.jp2')
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL to the Sipi server

    Returns:
        success status
    """
    xml_tree_orig = etree.parse(xml_file)
    pkl_files = get_pkl_files()
    orig_path_2_uuid_filename = _get_paths_from_pkl_files(pkl_files)
    xml_tree_replaced = replace_bitstream_paths(
        xml_tree=xml_tree_orig,
        orig_path_2_uuid_filename=orig_path_2_uuid_filename,
    )

    start_time = datetime.now()
    print(f"{start_time}: Start with fast XML upload...")

    xmlupload(
        input_file=xml_tree_replaced,
        server=dsp_url,
        user=user,
        password=password,
        imgdir=".",
        sipi=sipi_url,
        config=UploadConfig(preprocessing_done=True),
    )

    end_time = datetime.now()
    print(f"{end_time}: Total time of fast xml upload: {end_time - start_time}")
    return True
