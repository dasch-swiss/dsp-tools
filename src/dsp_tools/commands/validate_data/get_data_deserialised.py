import regex

from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def get_data_deserialised(resources: list[ParsedResource]) -> tuple[str, DataDeserialised]:
    pass


def _get_one_resource(resource: ParsedResource) -> ResourceDeserialised:
    pass


def _get_all_stand_off_links(values: list[ValueInformation]) -> list[PropertyObject]:
    stand_offs = []
    for val in values:
        if val.knora_type.RICHTEXT_VALUE:
            stand_offs.extend(_get_stand_off_links(val.user_facing_value))
    return stand_offs


def _get_stand_off_links(text: str | None) -> list[PropertyObject]:
    if not text:
        return []
    links = set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=text))
    return [PropertyObject(TriplePropertyType.KNORA_STANDOFF_LINK, lnk, TripleObjectType.IRI) for lnk in links]


def _get_one_value(value: ParsedValue) -> ValueInformation:
    match value.value_type:
        case KnoraValueType.LIST_VALUE:
            return _get_list_value(value)
        case KnoraValueType.INTERVAL_VALUE:
            return _get_interval_value(value)
        case _:
            return _get_generic_value(value)


def _get_generic_value(value: ParsedValue) -> ValueInformation:
    pass


def _get_list_value(value: ParsedValue) -> ValueInformation:
    pass


def _get_interval_value(value: ParsedValue) -> ValueInformation:
    pass


def _get_value_metadata(value: ParsedValue) -> list[PropertyObject]:
    pass


def _get_file_value(file_value: ParsedFileValue) -> ValueInformation:
    pass


def _get_file_metadata(metadata: ParsedFileValueMetadata) -> list[PropertyObject]:
    pass
