from lxml import etree

from dsp_tools.error.exceptions import BaseError
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.internal.file_values import AbstractFileValue
from dsp_tools.xmllib.models.internal.file_values import FileValue
from dsp_tools.xmllib.models.internal.file_values import IIIFUri
from dsp_tools.xmllib.models.internal.file_values import Metadata
from dsp_tools.xmllib.value_checkers import is_nonempty_value


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
        return _serialise_file_value(file_value, authorship_id, "bitstream")
    elif isinstance(file_value, IIIFUri):
        return _serialise_file_value(file_value, authorship_id, "iiif-uri")
    else:
        raise BaseError(
            f"file_value must be either a FileValue or a IIIFUri, but you provided {file_value.__class__.__name__}"
        )


def _serialise_file_value(value: AbstractFileValue, authorship_id: str, tag_name: str) -> etree._Element:
    attribs = _serialise_metadata(value.metadata, authorship_id)
    if is_nonempty_value(value.comment):
        attribs["comment"] = str(value.comment)
    ele = etree.Element(f"{DASCH_SCHEMA}{tag_name}", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
    ele.text = str(value.value)
    return ele


def _serialise_metadata(metadata: Metadata, authorship_id: str) -> dict[str, str]:
    attribs = {
        "license": str(metadata.license),
        "copyright-holder": metadata.copyright_holder,
        # the authorship that is contained in the metadata is the raw form, but we need its ID
        "authorship-id": authorship_id,
    }
    if metadata.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
        attribs["permissions"] = metadata.permissions.value
    return attribs
