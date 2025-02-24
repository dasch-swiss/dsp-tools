import pytest

from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _get_stand_off_links
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_link_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_one_resource
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import _process_richtext_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_deserialised_data import (
    create_info_for_graph_from_data,
)
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
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
        'This text contains a link: <a class="salsah-link" href="IRI:res_id_target:IRI">target resource</a>',
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
    return ResourceDeserialised("res_id", [], [link_value, text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_with_link(link_value: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised("res_id", [], [link_value], None, MigrationMetadata())


@pytest.fixture
def resource_with_text(text_value_with_link: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised("res_id", [], [text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_without_links() -> ResourceDeserialised:
    return ResourceDeserialised(
        "res_id_target",
        [],
        [ValueInformation("prop", "", KnoraValueType.SIMPLETEXT_VALUE, [])],
        None,
        MigrationMetadata(),
    )


def test_create_info_for_graph_from_data(
    resource_without_links: ResourceDeserialised, resource_with_link_and_text: ResourceDeserialised
) -> None:
    data = DataDeserialised([resource_with_link_and_text, resource_without_links])
    result = create_info_for_graph_from_data(data)
    assert set(result.all_resource_ids) == {"res_id_target", "res_id"}
    assert len(result.link_values) == 1
    assert len(result.standoff_links) == 1


def test_process_one_resource_no_links(resource_without_links: ResourceDeserialised) -> None:
    links, standoff = _process_one_resource(resource_without_links)
    assert not links
    assert not standoff


def test_process_one_resource_stand_off(
    resource_with_text: ResourceDeserialised, text_value_with_link: ValueInformation
) -> None:
    links, standoff_list = _process_one_resource(resource_with_text)
    assert not links
    assert len(standoff_list) == 1
    standoff = standoff_list.pop(0)
    assert standoff.source_id == "res_id"
    assert standoff.target_ids == {"res_id_target"}
    assert standoff.link_uuid == text_value_with_link.value_uuid


def test_process_one_resource_link_values(
    resource_with_link: ResourceDeserialised, link_value: ValueInformation
) -> None:
    link_list, standoff = _process_one_resource(resource_with_link)
    assert not standoff
    assert len(link_list) == 1
    link = link_list.pop(0)
    assert link.source_id == "res_id"
    assert link.target_id == "res_id_target"
    assert link.link_uuid == link_value.value_uuid


def test_process_one_resource_both_links(
    resource_with_link_and_text: ResourceDeserialised,
    link_value: ValueInformation,
    text_value_with_link: ValueInformation,
) -> None:
    link_list, standoff_list = _process_one_resource(resource_with_link_and_text)
    assert len(link_list) == 1
    link = link_list.pop(0)
    assert link.source_id == "res_id"
    assert link.target_id == "res_id_target"
    assert link.link_uuid == link_value.value_uuid

    assert len(standoff_list) == 1
    standoff = standoff_list.pop(0)
    assert standoff.source_id == "res_id"
    assert standoff.target_ids == {"res_id_target"}
    assert standoff.link_uuid == text_value_with_link.value_uuid


def test_process_link_value_with_links(link_value: ValueInformation) -> None:
    result = _process_link_value(link_value, "res_id")
    assert isinstance(result, LinkValueLink)
    assert result.source_id == "res_id"
    assert result.target_id == "res_id_target"
    assert result.link_uuid == link_value.value_uuid


def test_process_link_value_without_value() -> None:
    assert not _process_link_value(ValueInformation("prop", None, KnoraValueType.LINK_VALUE, []), "id")


def test_process_richtext_value_no_links(text_value_no_link: ValueInformation) -> None:
    assert not _process_richtext_value(text_value_no_link, "res_id")


def test_process_richtext_value_without_value() -> None:
    assert not _process_richtext_value(ValueInformation("prop", None, KnoraValueType.RICHTEXT_VALUE, []), "id")


def test_process_richtext_value_with_links(text_value_with_link: ValueInformation) -> None:
    result = _process_richtext_value(text_value_with_link, "res_id")
    assert isinstance(result, StandOffLink)
    assert result.source_id == "res_id"
    assert result.target_ids == {"res_id_target"}
    assert result.link_uuid == text_value_with_link.value_uuid


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('Internal Link: <a class="salsah-link" href="IRI:id:IRI">target res</a>', {"id"}),
        ('Resource IRI <a class="salsah-link" href="http://rdfh.ch/4123/DiAmY">IRI</a>', {"http://rdfh.ch/4123/DiAmY"}),
        ("None", None),
        (
            'Mixed Links: <a class="salsah-link" href="IRI:id:IRI">target res</a>, <a class="salsah-link" href="http://rdfh.ch/4123/DiAmY">IRI</a>',
            {"http://rdfh.ch/4123/DiAmY", "id"},
        ),
    ],
)
def test_get_stand_off_links(text: str, expected: set[str]) -> None:
    result = _get_stand_off_links(text)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
