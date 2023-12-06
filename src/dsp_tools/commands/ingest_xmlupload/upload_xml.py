from datetime import datetime
from pathlib import Path

from lxml import etree

from dsp_tools.commands.ingest_xmlupload.apply_ingest import get_mapping_dict_from_file, replace_bitstream_paths
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def ingest_xmlupload(
    xml_file: str,
    user: str,
    password: str,
    dsp_url: str,
    sipi_url: str,
) -> None:
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

    Raises:
        InputError: if any media was not uploaded of uploaded media was not referenced.
    """
    xml_tree_orig = etree.parse(xml_file)
    orig_path_2_uuid_filename = get_mapping_dict_from_file()
    xml_tree_replaced, ingest_message = replace_bitstream_paths(
        xml_tree=xml_tree_orig,
        orig_path_2_uuid_filename=orig_path_2_uuid_filename,
    )
    if good := ingest_message.all_good_msg():
        print(good)
        logger.info(good)
    else:
        err_msg = ingest_message.execute_error_protocol(Path(xml_file).absolute())
        logger.exception(err_msg)
        raise InputError(err_msg)

    start_time = datetime.now()
    print(f"{start_time}: Start with ingest xmlupload...")

    xmlupload(
        input_file=xml_tree_replaced,
        server=dsp_url,
        user=user,
        password=password,
        imgdir=".",
        sipi=sipi_url,
        config=UploadConfig(ingest_done=True),
    )

    end_time = datetime.now()
    print(f"{end_time}: Total time of ingest xmlupload: {end_time - start_time}")
