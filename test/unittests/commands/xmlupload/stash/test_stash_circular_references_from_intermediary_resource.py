from copy import deepcopy
from uuid import uuid4

import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.stash.stash_circular_references_from_intermediary_resource import (
    stash_circular_references,
)
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


@pytest.fixture
def resource_1() -> IntermediaryResource:
    link_value_to_resource_no_links = IntermediaryLink("res_no_links", "prop", None, None, str(uuid4()))
    link_value_with_permissions_to_res_2 = IntermediaryLink(
        "res_2", "prop", None, Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]}), "link_to_res_2_uuid"
    )
    simple_text_value = IntermediarySimpleText("Text", "prop", None, None)
    return IntermediaryResource(
        res_id="res_1",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[link_value_with_permissions_to_res_2, link_value_to_resource_no_links, simple_text_value],
    )


@pytest.fixture
def resource_2() -> IntermediaryResource:
    val = IntermediaryRichtext(
        FormattedTextValue('Link: <a class="salsah-link" href="IRI:res_3:IRI">res_3</a>'),
        "prop",
        None,
        None,
        set("res_3"),
        "standoff_link_to_res_3_uuid",
    )
    return IntermediaryResource(
        res_id="res_2",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[val],
    )


@pytest.fixture
def resource_3() -> IntermediaryResource:
    link_value_to_res_1 = IntermediaryLink("res_1", "prop", None, None, "link_to_res_1_uuid")
    return IntermediaryResource(
        res_id="res_3",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[link_value_to_res_1],
    )


@pytest.fixture
def resource_no_links() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="res_no_links",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[],
    )


def test_stash_circular_references_remove_link_value(
    resource_1: IntermediaryResource,
    resource_2: IntermediaryResource,
    resource_3: IntermediaryResource,
    resource_no_links: IntermediaryResource,
) -> None:
    copied_res_1 = deepcopy(resource_1)
    copied_res_2 = deepcopy(resource_2)
    copied_res_3 = deepcopy(resource_3)
    resources = [copied_res_1, copied_res_2, copied_res_3, deepcopy(resource_no_links)]
    lookup = {"res_1": ["link_to_res_2_uuid"]}
    result = stash_circular_references(resources, lookup)
    assert isinstance(result, Stash)
    assert not result.standoff_stash
    link_stash = result.link_value_stash
    assert isinstance(link_stash, LinkValueStash)
    assert link_stash.res_2_stash_items.keys() == lookup.keys()
    stash_list = link_stash.res_2_stash_items["res_1"]
    assert len(stash_list) == 1
    stash_item = stash_list.pop(0)
    assert stash_item.res_id == "res_1"
    assert stash_item.res_type == "type"
    assert stash_item.prop_name == "propValue"
    assert stash_item.target_id == "res_2"
    assert stash_item.permission == "CR knora-admin:ProjectAdmin"

    # check that the resource values are as expected
    assert len(copied_res_1.values) == 2
    content = {x.value for x in copied_res_1.values}
    assert content == {"res_no_links", "Text"}

    assert len(resource_2.values) == len(copied_res_2.values)
    assert len(resource_3.values) == len(copied_res_3.values)


def test_stash_circular_references_remove_text_value(
    resource_1: IntermediaryResource,
    resource_2: IntermediaryResource,
    resource_3: IntermediaryResource,
    resource_no_links: IntermediaryResource,
) -> None:
    copied_res_1 = deepcopy(resource_1)
    copied_res_2 = deepcopy(resource_2)
    copied_res_3 = deepcopy(resource_3)
    resources = [copied_res_1, copied_res_2, copied_res_3, deepcopy(resource_no_links)]
    lookup = {"res_2": ["standoff_link_to_res_3_uuid"]}
    result = stash_circular_references(resources, lookup)
    assert isinstance(result, Stash)
    assert not result.link_value_stash
    standoff_stash = result.standoff_stash
    assert isinstance(standoff_stash, StandoffStash)
    assert standoff_stash.res_2_stash_items.keys() == lookup.keys()
    stash_list = standoff_stash.res_2_stash_items["res_2"]
    assert len(stash_list) == 1
    stash_item = stash_list.pop(0)
    assert stash_item.res_id == "res_2"
    assert stash_item.res_type == "type"
    assert stash_item.uuid == "standoff_link_to_res_3_uuid"
    assert stash_item.prop_name == "prop"
    assert stash_item.value.xmlstr == 'Link: <a class="salsah-link" href="IRI:res_3:IRI">res_3</a>'

    # check that the resource values are as expected
    assert len(copied_res_2.values) == 1
    text_val = copied_res_2.values.pop(0)
    assert isinstance(text_val, IntermediaryRichtext)
    assert text_val.value.xmlstr == "standoff_link_to_res_3_uuid"
    assert len(resource_1.values) == len(copied_res_1.values)
    assert len(resource_3.values) == len(copied_res_3.values)


def test_stash_circular_references_no_stash(
    resource_1: IntermediaryResource,
) -> None:
    resources = [deepcopy(resource_1)]
    lookup: dict[str, list[str]] = {}
    assert not stash_circular_references(resources, lookup)


if __name__ == "__main__":
    pytest.main([__file__])
