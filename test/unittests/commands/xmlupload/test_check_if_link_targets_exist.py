import pytest

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.prepare_xml_input.check_if_link_targets_exist import _check_all_links

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"


@pytest.fixture
def richtext() -> IntermediaryRichtext:
    val = FormattedTextValue('<a class="salsah-link" href="IRI:target_resource_text:IRI">target_resource</a>')
    return IntermediaryRichtext(val, f"{ONTO}richtextPropValue", None, None, {"target_resource_text"}, "")


@pytest.fixture
def resource_richtext(richtext) -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_richtext",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[richtext, IntermediaryInt(1, f"{ONTO}intProp", None, None)],
    )


@pytest.fixture
def target_resource_text() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="target_resource_text", type_iri="type", label="lbl", permissions=None, values=[]
    )


@pytest.fixture
def resource_link_value() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_link_value",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[IntermediaryLink("target_resource_link", f"{ONTO}linkProp", None, None, "")],
    )


@pytest.fixture
def target_resource_link() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="target_resource_link", type_iri="type", label="lbl", permissions=None, values=[]
    )


def test_check_all_links_good(resource_richtext, resource_link_value, target_resource_text, target_resource_link):
    resources = [resource_richtext, resource_link_value, target_resource_text, target_resource_link]
    result = _check_all_links(resources)
    assert len(result) == 0


def test_check_all_links_missing_text(resource_richtext, resource_link_value, target_resource_link):
    resources = [resource_richtext, resource_link_value, target_resource_link]
    result = _check_all_links(resources)
    assert len(result) == 1
    expected = (
        "Resource 'resource_richtext', property 'onto:richtextPropValue' "
        "has a invalid standoff link target(s) 'target_resource_text'"
    )
    assert result[0] == expected


def test_check_all_links_missing_link(resource_richtext, resource_link_value, target_resource_text):
    resources = [resource_richtext, resource_link_value, target_resource_text]
    result = _check_all_links(resources)
    assert len(result) == 1
    expected = (
        "Resource 'resource_link_value', property 'onto:linkProp' has an invalid link target 'target_resource_link'"
    )
    assert result[0] == expected


if __name__ == "__main__":
    pytest.main([__file__])
