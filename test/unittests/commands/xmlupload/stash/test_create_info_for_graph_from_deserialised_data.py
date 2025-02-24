import pytest

from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_link_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_one_resource
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_richtext_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import (
    create_info_for_graph_from_data,
)
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


@pytest.fixture
def link_value() -> ValueInformation:
    return ValueInformation("prop", "res_id_target", KnoraValueType.LINK_VALUE, [])


@pytest.fixture
def text_value_with_link() -> ValueInformation:
    return ValueInformation(
        "prop",
        'This text contains a link: <a class="salsah-link" href="IRI:res_id_target:IRI">res_id_target</a>',
        KnoraValueType.RICHTEXT_VALUE,
        [],
    )


@pytest.fixture
def text_value_no_link() -> ValueInformation:
    return ValueInformation("prop", "Text", KnoraValueType.RICHTEXT_VALUE, [])


@pytest.fixture
def resource_with_link_and_text(
    link_value: ValueInformation, text_value_with_link: ValueInformation
) -> ResourceDeserialised:
    return ResourceDeserialised("res_id_link_text", [], [link_value, text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_with_link(link_value: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised("res_id_link", [], [link_value], None, MigrationMetadata())


@pytest.fixture
def resource_with_text(text_value_with_link: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised("res_id", [], [text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_with_no_links() -> ResourceDeserialised:
    return ResourceDeserialised(
        "res_id_target",
        [],
        [ValueInformation("prop", "", KnoraValueType.SIMPLETEXT_VALUE, [])],
        None,
        MigrationMetadata(),
    )


def test_create_info_for_graph_from_data(
    resource_with_no_links: ResourceDeserialised, resource_with_link_and_text: ResourceDeserialised
) -> None:
    data = DataDeserialised([resource_with_link_and_text, resource_with_no_links])
    result = create_info_for_graph_from_data(data)


def test_process_one_resource_no_links(resource_with_no_links: ResourceDeserialised) -> None:
    result = _process_one_resource(resource_with_no_links)


def test_process_one_resource_stand_off(resource_with_text: ResourceDeserialised) -> None:
    result = _process_one_resource(resource_with_text)


def test_process_one_resource_link_values(resource_with_link: ResourceDeserialised) -> None:
    result = _process_one_resource(resource_with_link)


def test_process_one_resource_both_links(resource_with_link_and_text: ResourceDeserialised) -> None:
    result = _process_one_resource(resource_with_link_and_text)


def test_process_richtext_value_no_links(text_value_no_link: ValueInformation) -> None:
    result = _process_richtext_value(text_value_no_link)


def test_process_richtext_value_with_links(text_value_with_link: ValueInformation) -> None:
    result = _process_richtext_value(text_value_with_link)


def test_process_link_value_with_links(link_value: ValueInformation) -> None:
    result = _process_link_value(link_value)


if __name__ == "__main__":
    pytest.main([__file__])
