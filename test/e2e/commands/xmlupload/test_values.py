# mypy: disable-error-code="no-untyped-def"


from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias
from test.e2e.commands.xmlupload.conftest import _util_get_res_iri_from_label

BASE_NUMBER_OF_TRIPLES_PER_VALUE = 9
OPEN_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
DOAP_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")


def _assert_number_of_values_is_one_and_get_val_iri(g: Graph, label: str, prop_iri: URIRef) -> SubjectObjectTypeAlias:
    res_iri = _util_get_res_iri_from_label(g, label)
    val_iri_list = list(g.objects(res_iri, prop_iri))
    assert len(val_iri_list) == 1
    return val_iri_list.pop(0)


class TestSharedTriples:
    def test_all_triples_of_a_value(self, class_with_everything_resource_graph, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(
            class_with_everything_resource_graph, "bool_true", prop_iri
        )
        val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
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
            assert len(list(class_with_everything_resource_graph.objects(val_iri, prp))) == 1
        assert len(val_triples) == len(props)

    def test_doap(self, class_with_everything_resource_graph, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(
            class_with_everything_resource_graph, "bool_true", prop_iri
        )
        permissions = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.hasPermissions))
        assert permissions == DOAP_PERMISSIONS

    def test_open_permissions(self, class_with_everything_resource_graph, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(
            class_with_everything_resource_graph, "bool_1_open_permissions_on_value", prop_iri
        )
        permissions = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.hasPermissions))
        assert permissions == OPEN_PERMISSIONS

    def test_comment_on_value(self, class_with_everything_resource_graph, onto_iri):
        prop_iri = URIRef(f"{onto_iri}testBoolean")
        val_iri = _assert_number_of_values_is_one_and_get_val_iri(
            class_with_everything_resource_graph, "bool_0_comment_on_value", prop_iri
        )
        val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
        cmnt = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.valueHasComment))
        assert cmnt == Literal("Comment on value")
        assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + 1


def test_bool_true(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testBoolean")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "bool_true", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal(True)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.booleanValueAsBoolean))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.BooleanValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_color(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testColor")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "color", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("#00ff00")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.colorValueAsColor))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.ColorValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_date(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testSubDate1")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "date", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("JULIAN:BCE:0700:BCE:0600")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.valueAsString))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.DateValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_decimal(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testDecimalSimpleText")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "decimal", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal(2.71)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.decimalValueAsDecimal))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.DecimalValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_geoname(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testGeoname")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "geoname", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("1111111")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.geonameValueAsGeonameCode))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.GeonameValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_integer(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testIntegerSimpleText")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "integer", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal(1)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.intValueAsInt))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.IntValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_list(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testListProp")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "list", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.listValueAsListNode))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.ListValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_link(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testHasLinkToValue")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "link", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    target_iri = _util_get_res_iri_from_label(class_with_everything_resource_graph, "resource_no_values")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.linkValueHasTargetIri))
    assert actual_value == target_iri
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.LinkValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_richtext(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testRichtext")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "richtext", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.textValueAsXml))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.TextValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE + 1


def test_textarea(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testTextarea")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "textarea", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("Line One\nLine Two")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.valueAsString))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.TextValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_simpletext(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}testSimpleText")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(
        class_with_everything_resource_graph, "simpletext", prop_iri
    )
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("Text")
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.valueAsString))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.TextValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_time(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "time", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.timeValueAsTimeStamp))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.TimeValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE


def test_uri(class_with_everything_resource_graph, onto_iri):
    prop_iri = URIRef(f"{onto_iri}")
    val_iri = _assert_number_of_values_is_one_and_get_val_iri(class_with_everything_resource_graph, "uri", prop_iri)
    val_triples = list(class_with_everything_resource_graph.triples((val_iri, None, None)))
    expected_val = Literal("https://dasch.swiss", datatype=XSD.anyURI)
    actual_value = next(class_with_everything_resource_graph.objects(val_iri, KNORA_API.uriValueAsUri))
    assert actual_value == expected_val
    assert next(class_with_everything_resource_graph.objects(val_iri, RDF.type)) == KNORA_API.UriValue
    assert len(val_triples) == BASE_NUMBER_OF_TRIPLES_PER_VALUE
