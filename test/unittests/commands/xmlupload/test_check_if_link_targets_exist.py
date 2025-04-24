# mypy: disable-error-code="method-assign,no-untyped-def"
import pytest
import regex

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInt
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.prepare_xml_input.check_if_link_targets_exist import check_if_link_targets_exist
from dsp_tools.error.exceptions import InputError

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"


@pytest.fixture
def resource_richtext() -> ProcessedResource:
    val = FormattedTextValue(
        '<a class="salsah-link" href="IRI:target_resource_text:IRI">target_resource</a> '
        'with IRI <a class="salsah-link" href="http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg">target existing IRI</a>'
    )
    richtext = ProcessedRichtext(val, f"{ONTO}richtextPropValue", None, None, {"target_resource_text"}, "")
    return ProcessedResource(
        res_id="resource_richtext",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[richtext, ProcessedInt(1, f"{ONTO}intProp", None, None)],
    )


@pytest.fixture
def resource_richtext_several() -> ProcessedResource:
    val = FormattedTextValue(
        'Text <a class="salsah-link" href="IRI:target_resource_text:IRI">target_resource_text</a> '
        'more text <a class="salsah-link" href="IRI:target_resource_link:IRI">target_resource_link</a>'
    )
    text = ProcessedRichtext(
        val, f"{ONTO}richtextPropValue", None, None, {"target_resource_text", "target_resource_link"}, ""
    )
    return ProcessedResource(
        res_id="resource_richtext",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[text],
    )


@pytest.fixture
def target_resource_text() -> ProcessedResource:
    return ProcessedResource(res_id="target_resource_text", type_iri="type", label="lbl", permissions=None, values=[])


@pytest.fixture
def resource_link_value() -> ProcessedResource:
    return ProcessedResource(
        res_id="resource_link_value",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[ProcessedLink("target_resource_link", f"{ONTO}linkProp", None, None, "")],
    )


@pytest.fixture
def resource_link_value_with_target_iri() -> ProcessedResource:
    return ProcessedResource(
        res_id="resource_link_value_with_target_iri",
        type_iri="type",
        label="lbl",
        permissions=None,
        values=[ProcessedLink("http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg", f"{ONTO}linkProp", None, None, "")],
    )


@pytest.fixture
def target_resource_link() -> ProcessedResource:
    return ProcessedResource(res_id="target_resource_link", type_iri="type", label="lbl", permissions=None, values=[])


def test_check_all_links_good(
    resource_richtext,
    resource_link_value,
    target_resource_text,
    target_resource_link,
    resource_link_value_with_target_iri,
):
    resources = [
        resource_richtext,
        resource_link_value,
        target_resource_text,
        target_resource_link,
        resource_link_value_with_target_iri,
    ]
    check_if_link_targets_exist(resources)


def test_check_all_links_missing_text(resource_richtext, resource_link_value, target_resource_link):
    resources = [resource_richtext, resource_link_value, target_resource_link]
    expected = regex.escape(
        "It is not possible to upload the XML file, because it contains invalid links:\n"
        " - Resource 'resource_richtext', property 'onto:richtextPropValue' "
        "has invalid standoff link targets: 'target_resource_text'"
    )
    with pytest.raises(InputError, match=expected):
        check_if_link_targets_exist(resources)


def test_check_all_links_missing_text_several(resource_richtext_several):
    resources = [resource_richtext_several]
    expected = regex.escape(
        "It is not possible to upload the XML file, because it contains invalid links:\n"
        " - Resource 'resource_richtext', property 'onto:richtextPropValue' "
        "has invalid standoff link targets: 'target_resource_link', 'target_resource_text'"
    )
    with pytest.raises(InputError, match=expected):
        check_if_link_targets_exist(resources)


def test_check_all_links_missing_link(resource_richtext, resource_link_value, target_resource_text):
    resources = [resource_richtext, resource_link_value, target_resource_text]
    expected = regex.escape(
        "It is not possible to upload the XML file, because it contains invalid links:\n"
        " - Resource 'resource_link_value', property 'onto:linkProp' has an invalid link target 'target_resource_link'"
    )
    with pytest.raises(InputError, match=expected):
        check_if_link_targets_exist(resources)


if __name__ == "__main__":
    pytest.main([__file__])
