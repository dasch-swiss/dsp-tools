# mypy: disable-error-code="no-untyped-def"
import pytest
import regex

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.utils.exceptions import DuplicateIdsInXmlAndId2IriMapping
from dsp_tools.utils.replace_id_with_iri import _process_link_value
from dsp_tools.utils.replace_id_with_iri import _process_one_resource
from dsp_tools.utils.replace_id_with_iri import _process_richtext_value
from dsp_tools.utils.replace_id_with_iri import _replace_all_ids_with_iris
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"
RES_TYPE = f"{ONTO}ResourceType"
RES_IRI = "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"


@pytest.fixture
def iri_resolver() -> IriResolver:
    return IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})


class TestReplaceAllIds:
    def test_all_good(self, iri_resolver):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _replace_all_ids_with_iris([res], iri_resolver)
        assert len(result) == 1

    def test_duplicate_ids(self, iri_resolver):
        res = ParsedResource(
            res_id="r1_id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        msg = regex.escape(
            "You provided a id2iri mapping file to replace IDs referenced in links and richtext "
            "with IRIs of previously uploaded resources. "
            "This means that the new XML file must not contain IDs that were previously used.\n"
            "The following ID(s) are both in the id2iri mapping and the new data: r1_id"
        )
        with pytest.raises(DuplicateIdsInXmlAndId2IriMapping, match=msg):
            _replace_all_ids_with_iris([res], iri_resolver)


class TestReplaceIdsWithIris:
    def test_with_values(self, iri_resolver):
        orig_list_val = ("list", "node")
        link_val = ParsedValue(HAS_PROP, "r1_id", KnoraValueType.LINK_VALUE, None, None)
        list_val = ParsedValue(HAS_PROP, orig_list_val, KnoraValueType.LIST_VALUE, "public", "cmt")
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[list_val, link_val],
            file_value=None,
            migration_metadata=None,
        )
        result = _process_one_resource(res, iri_resolver)
        assert len(result.values) == 2
        returned_list = next(iter([x for x in result.values if x.value_type == KnoraValueType.LIST_VALUE]))
        assert returned_list.value == orig_list_val
        returned_link = next(iter([x for x in result.values if x.value_type == KnoraValueType.LINK_VALUE]))
        assert returned_link.value == "r1_iri"

    def test_no_replacement(self, iri_resolver):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _process_one_resource(res, iri_resolver)
        assert not result.values


class TestProcessLinkValue:
    def test_in_lookup(self, iri_resolver):
        val = ParsedValue(HAS_PROP, "r1_id", KnoraValueType.LINK_VALUE, None, None)
        result = _process_link_value(val, iri_resolver)
        assert result.value == "r1_iri"

    def test_not_in_lookup(self, iri_resolver):
        val = ParsedValue(HAS_PROP, "other_id", KnoraValueType.LINK_VALUE, None, None)
        result = _process_link_value(val, iri_resolver)
        assert result.value == "other_id"


class TestProcessRichtextValue:
    def test_in_lookup(self, iri_resolver):
        text_str = 'Comment with <a class="salsah-link" href="IRI:r1_id:IRI">link text</a>.'
        val = ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, None, None)
        expected = 'Comment with <a class="salsah-link" href="r1_iri">link text</a>.'
        result = _process_richtext_value(val, iri_resolver)
        assert result.value == expected

    def test_not_in_lookup(self, iri_resolver):
        text_str = 'Comment with <a class="salsah-link" href="IRI:other:IRI">link text</a>.'
        val = ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, None, None)
        result = _process_richtext_value(val, iri_resolver)
        assert result.value == text_str

    def test_mixed(self, iri_resolver):
        text_str = (
            'This should be replaced <a class="salsah-link" href="IRI:r1_id:IRI">r1_id</a>. '
            'This remains <a class="salsah-link" href="IRI:other:IRI">other</a> now finished. '
            f'This is already an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.'
        )
        val = ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, None, None)
        expected = (
            'This should be replaced <a class="salsah-link" href="r1_iri">r1_id</a>. '
            'This remains <a class="salsah-link" href="IRI:other:IRI">other</a> now finished. '
            f'This is already an IRI <a class="salsah-link" href="{RES_IRI}">Resource IRI</a>.'
        )
        result = _process_richtext_value(val, iri_resolver)
        assert result.value == expected
