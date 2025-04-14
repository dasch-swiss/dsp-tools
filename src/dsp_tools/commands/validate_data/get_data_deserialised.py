from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def get_data_deserialised(resources: list[ParsedResource]) -> tuple[str, DataDeserialised]:
    pass


def _get_one_resource(resource: ParsedResource) -> ResourceDeserialised:
    pass


def _get_generic_value(value: ParsedValue) -> ValueInformation:
    pass


def _get_file_value(file_value: ParsedFileValue) -> ValueInformation:
    pass


def _get_file_metadata(metadata: ParsedFileValueMetadata) -> list[PropertyObject]:
    pass
