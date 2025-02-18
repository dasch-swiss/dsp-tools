from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.file_values import AbstractFileValue
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.value_checkers import is_string_like


def serialise_file_value(file_value: AbstractFileValue, authorship_id: str) -> etree._Element:
    """
    Serialise the file value of a resource.

    Args:
        file_value: File Value
        authorship_id: ID referencing the authorship

    Returns:
        File Value as etree

    Raises:
        BaseError: in case of an unknown class
    """
    if isinstance(file_value, FileValue):
        return _serialise_file_value(file_value, "bitstream")
    elif isinstance(file_value, IIIFUri):
        return _serialise_file_value(file_value, "iiif-uri")
    else:
        raise BaseError(
            f"file_value must be either a FileValue or a IIIFUri, but you provided {file_value.__class__.__name__}"
        )


def _serialise_file_value(value: AbstractFileValue, tag_name: str) -> etree._Element:
    attribs = {}
    if value.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = value.permissions.value
    if is_string_like(value.comment):
        attribs["comment"] = str(value.comment)
    ele = etree.Element(f"{DASCH_SCHEMA}{tag_name}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
    ele.text = str(value.value)
    return ele
