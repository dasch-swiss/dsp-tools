import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import _get_stand_off_links
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import _process_link_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import _process_one_resource
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import _process_richtext_value
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import (
    create_info_for_graph_from_data,
)
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


@pytest.fixture
def link_value() -> IntermediaryValue:
    return IntermediaryLink("res_id_target", "prop", None, None)


@pytest.fixture
def text_value_with_link() -> IntermediaryValue:
    return IntermediaryRichtext(
        FormattedTextValue(
            'This text contains a link: <a class="salsah-link" href="IRI:res_id_target:IRI">target resource</a>'
        ),
        "prop",
        None,
        None,
        {"res_id_target"},
    )


@pytest.fixture
def text_value_no_link() -> IntermediaryValue:
    return IntermediaryRichtext(FormattedTextValue("Text"), "prop", None, None, set())


@pytest.fixture
def resource_with_link_and_text(
    link_value: IntermediaryValue, text_value_with_link: IntermediaryValue
) -> IntermediaryResource:
    return IntermediaryResource("res_id", [], [link_value, text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_with_link(link_value: IntermediaryValue) -> IntermediaryResource:
    return IntermediaryResource("res_id", [], [link_value], None, MigrationMetadata())


@pytest.fixture
def resource_with_text(text_value_with_link: IntermediaryValue) -> IntermediaryResource:
    return IntermediaryResource("res_id", [], [text_value_with_link], None, MigrationMetadata())


@pytest.fixture
def resource_without_links() -> IntermediaryResource:
    return IntermediaryResource(
        "res_id_target",
        [],
        [ValueInformation("prop", "", KnoraValueType.SIMPLETEXT_VALUE, [])],
        None,
        MigrationMetadata(),
    )


def test_create_info_for_graph_from_data(
    resource_without_links: IntermediaryResource, resource_with_link_and_text: IntermediaryResource
) -> None:
    data = DataDeserialised([resource_with_link_and_text, resource_without_links])
    result = create_info_for_graph_from_data(data)
    assert set(result.all_resource_ids) == {"res_id_target", "res_id"}
    assert len(result.link_values) == 1
    assert len(result.standoff_links) == 1


def test_process_one_resource_no_links(resource_without_links: IntermediaryResource) -> None:
    links, standoff = _process_one_resource(resource_without_links)
    assert not links
    assert not standoff


def test_process_one_resource_stand_off(
    resource_with_text: IntermediaryValue, text_value_with_link: IntermediaryValue
) -> None:
    links, standoff_list = _process_one_resource(resource_with_text)
    assert not links
    assert len(standoff_list) == 1
    standoff = standoff_list.pop(0)
    assert standoff.source_id == "res_id"
    assert standoff.target_ids == {"res_id_target"}
    assert standoff.link_uuid == text_value_with_link.value_uuid


def test_process_one_resource_link_values(
    resource_with_link: IntermediaryResource, link_value: IntermediaryValue
) -> None:
    link_list, standoff = _process_one_resource(resource_with_link)
    assert not standoff
    assert len(link_list) == 1
    link = link_list.pop(0)
    assert link.source_id == "res_id"
    assert link.target_id == "res_id_target"
    assert link.link_uuid == link_value.value_uuid


def test_process_one_resource_both_links(
    resource_with_link_and_text: IntermediaryResource,
    link_value: IntermediaryValue,
    text_value_with_link: IntermediaryValue,
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


def test_process_link_value_with_links(link_value: IntermediaryValue) -> None:
    result = _process_link_value(link_value, "res_id")
    assert isinstance(result, LinkValueLink)
    assert result.source_id == "res_id"
    assert result.target_id == "res_id_target"
    assert result.link_uuid == link_value.value_uuid


def test_process_link_value_without_value() -> None:
    assert not _process_link_value(IntermediaryLink("prop", None, KnoraValueType.LINK_VALUE, []), "id")


def test_process_richtext_value_no_links(text_value_no_link: IntermediaryValue) -> None:
    assert not _process_richtext_value(text_value_no_link, "res_id")


def test_process_richtext_value_without_value() -> None:
    assert not _process_richtext_value(IntermediaryRichtext("prop", None, KnoraValueType.RICHTEXT_VALUE, []), "id")


def test_process_richtext_value_with_links(text_value_with_link: IntermediaryValue) -> None:
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
