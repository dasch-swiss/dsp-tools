# mypy: disable-error-code="no-untyped-def"
import json
import urllib.parse
from typing import cast

import pytest
import requests
from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias
from test.e2e.commands.xmlupload.utils import util_get_res_iri_from_label
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

BASE_NUMBER_OF_TRIPLES_PER_VALUE = 9
OPEN_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
DOAP_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")


@pytest.fixture(scope="module")
def g_minimal(_xmlupload_minimal_correct, class_with_everything_iri, auth_header, project_iri, creds) -> Graph:
    return util_request_resources_by_class(class_with_everything_iri, auth_header, project_iri, creds)


def _assert_number_of_values_is_one_and_get_val_iri(g: Graph, label: str, prop_iri: URIRef) -> SubjectObjectTypeAlias:
    res_iri = util_get_res_iri_from_label(g, label)
    val_iri_list = list(g.objects(res_iri, prop_iri))
    assert len(val_iri_list) == 1
    return val_iri_list.pop(0)


class TestSharedTriples:
    """
    The xmlupload code that creates metadata triples (e.g. the permissions) is shared by all value types.
    These generic triples are tested only once and not for each value type individually.
    """

    def test_all_triples_of_a_value(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "bool_true", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        props = [
            KNORA_API.arkUrl,
            KNORA_API.versionArkUrl,
            KNORA_API.userHasPermission,
            KNORA_API.attachedToUser,
            KNORA_API.valueHasUUID,
            KNORA_API.hasPermissions,
            RDF.type,
            KNORA_API.booleanValueAsBoolean,
            KNORA_API.valueCreationDate,
        ]
        for prp in props:
            assert len(list(g_minimal.objects(val_iri, prp))) == 1
        assert len(val_triples) == len(props)

    def test_doap(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "bool_true", prop_iri)
        permissions = next(g_minimal.objects(val_iri, KNORA_API.hasPermissions))
        assert permissions == DOAP_PERMISSIONS

    def test_open_permissions(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(
            g_minimal, "bool_1_open_permissions_on_value", prop_iri
        )
        permissions = next(g_minimal.objects(val_iri, KNORA_API.hasPermissions))
        assert permissions == OPEN_PERMISSIONS

    def test_comment_on_value(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "bool_0_comment_on_value", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        cmnt = next(g_minimal.objects(val_iri, KNORA_API.valueHasComment))
        assert cmnt == Literal("Comment on value")
        comment_triple = 1
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + comment_triple


class TestValues:
    """
    The following tests, test the triples that are specific to each value type.
    """

    def test_bool_true(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "bool_true", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal(True)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.booleanValueAsBoolean))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.BooleanValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_color(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testColor")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "color", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("#00ff00")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.colorValueAsColor))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.ColorValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_date(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testSubDate1")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "date", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("JULIAN:0700 BCE:0600 BCE")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.valueAsString))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.DateValue
        date_details = [
            (KNORA_API.dateValueHasCalendar, Literal("JULIAN")),
            (KNORA_API.dateValueHasStartEra, Literal("BCE")),
            (KNORA_API.dateValueHasStartYear, Literal("700", datatype=XSD.integer)),
            (KNORA_API.dateValueHasEndEra, Literal("BCE")),
            (KNORA_API.dateValueHasEndYear, Literal("600", datatype=XSD.integer)),
        ]
        for prp, val in date_details:
            assert next(g_minimal.objects(val_iri, prp)) == val
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + len(date_details)

    def test_decimal(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testDecimalSimpleText")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "decimal", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("2.71", datatype=XSD.decimal)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.decimalValueAsDecimal))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.DecimalValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_geometry(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}Region"
        res_g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(res_g, "region", KNORA_API.hasGeometry)
        val_triples = list(res_g.triples((val_iri, None, None)))
        actual_value = str(next(res_g.objects(val_iri, KNORA_API.geometryValueAsGeometry)))
        geom_json = json.loads(actual_value)
        assert set(geom_json.keys()) == {"status", "type", "lineWidth", "points"}
        assert next(res_g.objects(val_iri, RDF.type)) == KNORA_API.GeomValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_geoname(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testGeoname")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "geoname", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("1111111")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.geonameValueAsGeonameCode))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.GeonameValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_integer(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testIntegerSimpleText")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "integer", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal(1)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.intValueAsInt))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.IntValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_interval(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}AudioSegment"
        res_g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(res_g, "audio_segment", KNORA_API.hasSegmentBounds)
        val_triples = list(res_g.triples((val_iri, None, None)))
        interval_start = Literal("0.1", datatype=XSD.decimal)
        actual_interval_start = next(res_g.objects(val_iri, KNORA_API.intervalValueHasStart))
        assert actual_interval_start == interval_start
        interval_end = Literal("0.2", datatype=XSD.decimal)
        actual_interval_end = next(res_g.objects(val_iri, KNORA_API.intervalValueHasEnd))
        assert actual_interval_end == interval_end
        assert next(res_g.objects(val_iri, RDF.type)) == KNORA_API.IntervalValue
        additional_interval_triple = 1
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + additional_interval_triple

    def _util_get_list_node(self, creds, auth_header) -> str:
        all_lists_one_project_endpoint = f"{creds.server}/admin/lists?9999"
        headers = auth_header | {"Content-Type": "application/json"}
        response_all_lists = requests.get(all_lists_one_project_endpoint, timeout=3, headers=headers).json()
        first_list = next(x for x in response_all_lists["lists"] if x["name"] == "firstList")
        list_iri = urllib.parse.quote_plus(first_list["id"])
        all_nodes_one_list_endpoint = f"{creds.server}/admin/lists/{list_iri}"
        response_all_nodes = requests.get(all_nodes_one_list_endpoint, timeout=3, headers=headers).json()
        children = response_all_nodes["list"]["children"]
        node_one = list(x for x in children if x["name"] == "n1")
        assert len(node_one) == 1
        return cast(str, node_one.pop(0)["id"])

    def test_list(self, g_minimal, onto_iri, creds, auth_header):
        prop_iri = URIRef(f"{onto_iri}testListProp")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "list", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        list_node_iri = self._util_get_list_node(creds, auth_header)
        expected_val = URIRef(list_node_iri)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.listValueAsListNode))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.ListValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_link(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testHasLinkToValue")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "link", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        target_iri = util_get_res_iri_from_label(g_minimal, "resource_no_values")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.linkValueHasTargetIri))
        assert actual_value == target_iri
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.LinkValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_richtext(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testRichtext")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "richtext", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal('<?xml version="1.0" encoding="UTF-8"?>\n<text><p> Text </p></text>')
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.textValueAsXml))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.TextValue
        text_type = next(g_minimal.objects(val_iri, KNORA_API.hasTextValueType))
        assert text_type == KNORA_API.FormattedText
        mapping_type = next(g_minimal.objects(val_iri, KNORA_API.textValueHasMapping))
        assert mapping_type == URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")
        additional_richtext_triples = 2
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + additional_richtext_triples

    def test_textarea(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testTextarea")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "textarea", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("Line One\nLine Two")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.valueAsString))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.TextValue
        text_type = next(g_minimal.objects(val_iri, KNORA_API.hasTextValueType))
        assert text_type == KNORA_API.UnformattedText
        additional_text_type_triple = 1
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + additional_text_type_triple

    def test_simpletext(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testSimpleText")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "simpletext", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("Text")
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.valueAsString))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.TextValue
        text_type = next(g_minimal.objects(val_iri, KNORA_API.hasTextValueType))
        assert text_type == KNORA_API.UnformattedText
        additional_text_type_triple = 1
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + additional_text_type_triple

    def test_time(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testTimeValue")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "time", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("2019-10-24T03:45:12.010Z", datatype=XSD.dateTimeStamp)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.timeValueAsTimeStamp))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.TimeValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE

    def test_uri(self, g_minimal, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testUriValue")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(g_minimal, "uri", prop_iri)
        val_triples = list(g_minimal.triples((val_iri, None, None)))
        expected_val = Literal("https://dasch.swiss", datatype=XSD.anyURI)
        actual_value = next(g_minimal.objects(val_iri, KNORA_API.uriValueAsUri))
        assert actual_value == expected_val
        assert next(g_minimal.objects(val_iri, RDF.type)) == KNORA_API.UriValue
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE
