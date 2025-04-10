import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.prepare_xml_input.check_if_link_targets_exist import _check_all_links


@pytest.fixture
def richtext() -> IntermediaryRichtext:
    val = FormattedTextValue('<a class="salsah-link" href="IRI:target_resource_text:IRI">target_resource</a>')
    return IntermediaryRichtext(val, "richtextProp", None, None, {"target_resource_text"}, "")


@pytest.fixture
def resource_richtext(richtext) -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_richtext",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[richtext, IntermediaryInt(1, "intProp", None, None)],
    )


@pytest.fixture
def target_resource_text() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="target_resource_text", type_iri="type", label="lbl", permissions=None, values=[]
    )


@pytest.fixture
def resource_link_value() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_richtext",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[IntermediaryLink("target_resource_link", "linkProp", None, None, "")],
    )


@pytest.fixture
def target_resource_link() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="target_resource_link", type_iri="type", label="lbl", permissions=None, values=[]
    )


def test_check_all_links_good(richtext, resource_link_value, target_resource_text, target_resource_link):
    resources = [richtext, resource_link_value, target_resource_text, target_resource_link]
    assert len(_check_all_links(resources)) == 0


def test_check_all_links_missing_text(richtext, resource_link_value, target_resource_link):
    resources = [richtext, resource_link_value, target_resource_link]
    assert len(_check_all_links(resources)) == 0


def test_check_all_links_missing_link(richtext, resource_link_value, target_resource_text):
    resources = [richtext, resource_link_value, target_resource_text]
    assert len(_check_all_links(resources)) == 0


if __name__ == "__main__":
    pytest.main([__file__])
