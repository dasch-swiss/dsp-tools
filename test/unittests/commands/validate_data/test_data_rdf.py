from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ColorValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DateValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import IntValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import LinkValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ListValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import ResourceRDF
from dsp_tools.commands.validate_data.models.data_rdf import RichtextRDF
from dsp_tools.commands.validate_data.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.validate_data.models.data_rdf import TimeValueRDF
from dsp_tools.commands.validate_data.models.data_rdf import UriValueRDF
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


class TestResource:
    def test_with_value(self, rdf_resource: ResourceRDF) -> None:
        g = rdf_resource.make_graph()
        assert len(g) == 2
        out_res_id = next(g.subjects(RDF.type, ONTO.ClassWithEverything))
        assert out_res_id == rdf_resource.res_iri
        lbl = next(g.objects(out_res_id, RDFS.label))
        assert lbl == Literal("lbl", datatype=XSD.string)


class TestBooleanValue:
    def test_make_graph_corr(self, rdf_boolean_value_corr: BooleanValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_boolean_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.BooleanValue))
        bn_prop = next(g.subjects(KNORA_API.booleanValueAsBoolean))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testBoolean, bn_type))
        assert res_id == in_id


class TestColorValue:
    def test_make_graph_corr(self, rdf_color_value_corr: ColorValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_color_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.ColorValue))
        bn_prop = next(g.subjects(KNORA_API.colorValueAsColor))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testColor, bn_type))
        assert res_id == in_id


class TestDateValueRDF:
    def test_make_graph_corr(self, rdf_date_value_corr: DateValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_date_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.DateValue))
        bn_prop = next(g.subjects(KNORA_API.valueAsString))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testSubDate1, bn_type))
        assert res_id == in_id


class TestDecimalValue:
    def test_make_graph_corr(self, rdf_decimal_value_corr: DecimalValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_decimal_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.DecimalValue))
        bn_prop = next(g.subjects(KNORA_API.decimalValueAsDecimal))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testDecimalSimpleText, bn_type))
        assert res_id == in_id


class TestGeonameValue:
    def test_make_graph_corr(self, rdf_geoname_value_corr: GeonameValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_geoname_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.GeonameValue))
        bn_prop = next(g.subjects(KNORA_API.geonameValueAsGeonameCode))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testGeoname, bn_type))
        assert res_id == in_id


class TestIntValue:
    def test_make_graph_corr(self, rdf_integer_value_corr: IntValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_integer_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.IntValue))
        bn_prop = next(g.subjects(KNORA_API.intValueAsInt))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testIntegerSimpleText, bn_type))
        assert res_id == in_id


class TestLinkValue:
    def test_make_graph_corr(self, rdf_link_value_corr: LinkValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_link_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.LinkValue))
        bn_prop = next(g.subjects(API_SHAPES.linkValueHasTargetID))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testHasLinkTo, bn_type))
        assert res_id == in_id


class TestListValue:
    def test_make_graph_corr(self, rdf_list_value_corr: ListValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_list_value_corr.make_graph()
        assert len(g) == 4
        bn_type = next(g.subjects(RDF.type, KNORA_API.ListValue))
        bn_prop = next(g.subjects(API_SHAPES.listNodeAsString))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testListProp, bn_type))
        assert res_id == in_id


class TestRichtext:
    def test_make_graph_corr(self, rdf_text_richtext_value_corr: RichtextRDF) -> None:
        in_id = URIRef("id")
        g = rdf_text_richtext_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.TextValue))
        bn_prop = next(g.subjects(KNORA_API.textValueAsXml))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testRichtext, bn_type))
        assert res_id == in_id


class TestSimpleText:
    def test_make_graph_corr(self, rdf_text_simpletext_value_corr: SimpleTextRDF) -> None:
        in_id = URIRef("id")
        g = rdf_text_simpletext_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.TextValue))
        bn_prop = next(g.subjects(KNORA_API.valueAsString))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testTextarea, bn_type))
        assert res_id == in_id


class TestTimeValue:
    def test_make_graph_corr(self, rdf_time_value_corr: TimeValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_time_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.TimeValue))
        bn_prop = next(g.subjects(KNORA_API.timeValueAsTimeStamp))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testTimeValue, bn_type))
        assert res_id == in_id


class TestUriValue:
    def test_make_graph_corr(self, rdf_uri_value_corr: UriValueRDF) -> None:
        in_id = URIRef("id")
        g = rdf_uri_value_corr.make_graph()
        assert len(g) == 3
        bn_type = next(g.subjects(RDF.type, KNORA_API.UriValue))
        bn_prop = next(g.subjects(KNORA_API.uriValueAsUri))
        assert bn_type == bn_prop
        res_id = next(g.subjects(ONTO.testUriValue, bn_type))
        assert res_id == in_id
