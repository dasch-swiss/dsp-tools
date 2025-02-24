from copy import deepcopy
from uuid import uuid4

import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.stash.stash_circular_references_from_intermediary_resource import (
    stash_circular_references,
)


@pytest.fixture
def link_value_with_permissions_to_res_1() -> IntermediaryLink:
    return IntermediaryLink(
        "res_1", "prop", None, Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]}), str(uuid4())
    )


@pytest.fixture
def link_value_no_permissions_to_res_2() -> IntermediaryLink:
    return IntermediaryLink("res_2", "prop", None, None, str(uuid4()))


@pytest.fixture
def link_value_to_resource_no_links() -> IntermediaryLink:
    return IntermediaryLink("res_no_links", "prop", None, None, str(uuid4()))


@pytest.fixture
def text_value_no_links() -> IntermediaryRichtext:
    return IntermediaryRichtext(FormattedTextValue("No links"), "prop", None, None, set(), str(uuid4()))


@pytest.fixture
def text_value_with_link() -> IntermediaryRichtext:
    return IntermediaryRichtext(
        FormattedTextValue('Link: <a class="salsah-link" href="IRI:res_3:IRI">res_3</a>'),
        "prop",
        None,
        None,
        set("res_3"),
        str(uuid4()),
    )


@pytest.fixture
def resource_1(
    link_value_no_permissions_to_res_2: IntermediaryLink, link_value_to_resource_no_links: IntermediaryLink
) -> IntermediaryResource:
    return IntermediaryResource(
        res_id="res_1",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[link_value_no_permissions_to_res_2, link_value_to_resource_no_links],
    )


@pytest.fixture
def resource_2(text_value_with_link: IntermediaryRichtext) -> IntermediaryResource:
    return IntermediaryResource(
        res_id="res_2",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[text_value_with_link],
    )


@pytest.fixture
def resource_3(link_value_with_permissions_to_res_1: IntermediaryRichtext) -> IntermediaryResource:
    return IntermediaryResource(
        res_id="res_3",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[link_value_with_permissions_to_res_1],
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
    resources = [deepcopy(resource_1), deepcopy(resource_2), deepcopy(resource_3), deepcopy(resource_no_links)]
    lookup = {}
    stash = stash_circular_references(resources, lookup)


def test_stash_circular_references_remove_text_value(
    resource_1: IntermediaryResource,
    resource_2: IntermediaryResource,
    resource_3: IntermediaryResource,
    resource_no_links: IntermediaryResource,
) -> None:
    resources = [deepcopy(resource_1), deepcopy(resource_2), deepcopy(resource_3), deepcopy(resource_no_links)]
    lookup = {}
    stash = stash_circular_references(resources, lookup)


if __name__ == "__main__":
    pytest.main([__file__])
