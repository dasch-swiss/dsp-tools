from __future__ import annotations

from pathlib import Path

from lxml import etree

from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import replace_filepath_with_sipi_id
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree

logger = get_logger(__name__)


def ingest_xmlupload(
    xml_file: Path,
    user: str,
    password: str,
    dsp_url: str,
    sipi_url: str,
    interrupt_after: int | None = None,
) -> None:
    """
    This function reads an XML file
    and imports the data described in it onto the DSP server,
    using the ingest XML upload method.
    Before using this function,
    the multimedia files must be ingested on the DSP server.
    A mapping file with the internal IDs of the multimedia files must also be provided.

    Args:
        xml_file: path to XML file containing the resources
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL to the Sipi server
        interrupt_after: if set, the upload will be interrupted after this number of resources

    Raises:
        InputError: if any media was not uploaded or uploaded media was not referenced.
    """
    xml_tree_orig = etree.parse(xml_file)
    xml_tree_orig = remove_comments_from_element_tree(xml_tree_orig)

    shortcode = xml_tree_orig.getroot().attrib["shortcode"]
    orig_path_2_id_filename = get_mapping_dict_from_file(shortcode)
    xml_tree_replaced, ingest_info = replace_filepath_with_sipi_id(
        xml_tree=xml_tree_orig,
        orig_path_2_id_filename=orig_path_2_id_filename,
    )
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise InputError(err_msg)

    xmlupload(
        input_file=xml_tree_replaced,
        server=dsp_url,
        user=user,
        password=password,
        imgdir=".",
        sipi=sipi_url,
        config=UploadConfig(media_previously_uploaded=True, interrupt_after=interrupt_after),
    )
