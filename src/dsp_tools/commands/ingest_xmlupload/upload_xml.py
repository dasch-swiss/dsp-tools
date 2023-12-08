from datetime import datetime

from lxml import etree

from dsp_tools.commands.ingest_xmlupload.apply_ingest import get_mapping_dict_from_file, replace_filepath_with_sipi_uuid
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
    and uploaded by the upload step.

    Args:
        xml_file: path to XML file containing the resources
        user: the user's e-mail for login into DSP
        password: the user's password for login into DSP
        dsp_url: URL to the DSP server
        sipi_url: URL to the Sipi server

    Raises:
        InputError: if any media was not uploaded of uploaded media was not referenced.
    """
    xml_tree_orig = etree.parse(xml_file)
    orig_path_2_uuid_filename = get_mapping_dict_from_file()
    xml_tree_replaced, ingest_message = replace_filepath_with_sipi_uuid(
        xml_tree=xml_tree_orig,
        orig_path_2_uuid_filename=orig_path_2_uuid_filename,
    )
    if good := ingest_message.all_good_msg():
        print(good)
        logger.info(good)
    else:
        err_msg = ingest_message.execute_error_protocol()
        logger.exception(err_msg)
        raise InputError(err_msg)

    start_time = datetime.now()
    print(f"{start_time}: Start with ingest-xmlupload...")

    xmlupload(
        input_file=xml_tree_replaced,
        server=dsp_url,
        user=user,
        password=password,
        imgdir=".",
        sipi=sipi_url,
        config=UploadConfig(do_ingest_xmlupload=True),
    )

    end_time = datetime.now()
    print(f"{end_time}: Total time of ingest-xmlupload: {end_time - start_time}")
