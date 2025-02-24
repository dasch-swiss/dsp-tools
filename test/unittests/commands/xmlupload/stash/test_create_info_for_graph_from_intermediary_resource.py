from uuid import uuid4

import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import _process_one_resource
from dsp_tools.commands.xmlupload.stash.create_info_for_graph_from_intermediary_resource import (
    create_info_for_graph_from_intermediary_resources,
)


@pytest.fixture
def link_value() -> IntermediaryValue:
    return IntermediaryLink("res_id_target", "prop", None, None, str(uuid4()))


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
        str(uuid4()),
    )


@pytest.fixture
def text_value_no_link() -> IntermediaryValue:
    return IntermediaryRichtext(FormattedTextValue("Text"), "prop", None, None, set(), str(uuid4()))


@pytest.fixture
def resource_with_link_and_text(
    link_value: IntermediaryValue, text_value_with_link: IntermediaryValue
) -> IntermediaryResource:
    return IntermediaryResource("res_id", "res_type", "lbl", None, [link_value, text_value_with_link])


@pytest.fixture
def resource_with_link(link_value: IntermediaryValue) -> IntermediaryResource:
    return IntermediaryResource("res_id", "res_type", "lbl", None, [link_value])


@pytest.fixture
def resource_with_text(text_value_with_link: IntermediaryValue) -> IntermediaryResource:
    return IntermediaryResource("res_id", "res_type", "lbl", None, [text_value_with_link])


@pytest.fixture
def resource_without_links() -> IntermediaryResource:
    return IntermediaryResource(
        "res_id_target",
        "res_type",
        "lbl",
        None,
        [IntermediarySimpleText("val", "prop", None, None)],
    )


def test_create_info_for_graph_from_data(
    resource_without_links: IntermediaryResource, resource_with_link_and_text: IntermediaryResource
) -> None:
    data = [resource_with_link_and_text, resource_without_links]
    result = create_info_for_graph_from_intermediary_resources(data)
    assert set(result.all_resource_ids) == {"res_id_target", "res_id"}
    assert len(result.link_values) == 1
    assert len(result.standoff_links) == 1


def test_process_one_resource_no_links(resource_without_links: IntermediaryResource) -> None:
    links, standoff = _process_one_resource(resource_without_links)
    assert not links
    assert not standoff


def test_process_one_resource_stand_off(
    resource_with_text: IntermediaryResource, text_value_with_link: IntermediaryRichtext
) -> None:
    links, standoff_list = _process_one_resource(resource_with_text)
    assert not links
    assert len(standoff_list) == 1
    standoff = standoff_list.pop(0)
    assert standoff.source_id == "res_id"
    assert standoff.target_ids == {"res_id_target"}
    assert standoff.link_uuid == text_value_with_link.value_uuid


def test_process_one_resource_link_values(
    resource_with_link: IntermediaryResource, link_value: IntermediaryLink
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
    link_value: IntermediaryLink,
    text_value_with_link: IntermediaryRichtext,
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


if __name__ == "__main__":
    pytest.main([__file__])
