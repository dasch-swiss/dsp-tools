from dsp_tools.xmllib.models.file_values import IIIFUri, AbstractFileValue, FileValue
from typing import assert_never, Never, cast
from dsp_tools.xmllib.constants import DASCH_SCHEMA
from dsp_tools.xmllib.constants import XML_NAMESPACE_MAP
from lxml import etree

def serialise_file_value(file_value: AbstractFileValue) -> etree._Element:
    if isinstance(file_value, FileValue):
        pass
    elif isinstance(file_value, IIIFUri):
        pass
    else:
        never: Never = cast(Never, file_value)
        assert_never(never)


def _serialise_file_value(value: FileValue) -> etree._Element:
    pass

def _serialise_iiif_uri(value: IIIFUri) -> etree._Element:
    pass


def _get_metadata_attributes(value: AbstractFileValue) -> dict[str, str]:
    pass