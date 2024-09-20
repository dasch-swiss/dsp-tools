import pytest
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ColorValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DateValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import IntValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import LinkValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ListValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ResourceRDF
from dsp_tools.commands.xml_validate.models.data_rdf import RichtextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import TimeValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import UriValueRDF


@pytest.fixture
def resource_empty() -> ResourceRDF:
    return ResourceRDF(
        res_id=URIRef("id"),
        res_class=URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"),
        label=Literal("lbl", datatype=XSD.string),
        values=[],
    )


@pytest.fixture
def root_resource_with_props(boolean_value_corr: BooleanValueRDF) -> ResourceRDF:
    return ResourceRDF(
        res_id=URIRef("id"),
        res_class=URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"),
        label=Literal("lbl", datatype=XSD.string),
        values=[boolean_value_corr],
    )


@pytest.fixture
def root_resource_region() -> ResourceRDF:
    return ResourceRDF(
        res_id=URIRef("id"),
        res_class=URIRef("http://api.knora.org/ontology/knora-api/v2#Region"),
        label=Literal("lbl", datatype=XSD.string),
        values=[],
    )


@pytest.fixture
def boolean_value_corr() -> BooleanValueRDF:
    return BooleanValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean"), Literal("false", datatype=XSD.boolean)
    )


@pytest.fixture
def boolean_value_empty() -> BooleanValueRDF:
    return BooleanValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def color_value_corr() -> ColorValueRDF:
    return ColorValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"), Literal("00ff00", datatype=XSD.string)
    )


@pytest.fixture
def date_value_corr() -> DateValueRDF:
    return DateValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"),
        Literal("JULIAN:BCE:0700:BCE:0600", datatype=XSD.string),
    )


@pytest.fixture
def decimal_value_corr() -> DecimalValueRDF:
    return DecimalValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"), Literal("1.2", datatype=XSD.decimal)
    )


@pytest.fixture
def decimal_value_empty() -> DecimalValueRDF:
    return DecimalValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def geoname_value_corr() -> GeonameValueRDF:
    return GeonameValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"), Literal("1241345", datatype=XSD.integer)
    )


@pytest.fixture
def integer_value_corr() -> IntValueRDF:
    return IntValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"), Literal("1", datatype=XSD.integer)
    )


@pytest.fixture
def integer_value_empty() -> IntValueRDF:
    return IntValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def link_value_corr() -> LinkValueRDF:
    return LinkValueRDF(URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"), URIRef("link-id"))


@pytest.fixture
def link_value_empty() -> LinkValueRDF:
    return LinkValueRDF(URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"), URIRef(""))


@pytest.fixture
def list_value_corr() -> ListValueRDF:
    return ListValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"),
        object_value=Literal("n1", datatype=XSD.string),
        list_name=Literal("onlyList", datatype=XSD.string),
    )


@pytest.fixture
def list_value_wrong_node() -> ListValueRDF:
    return ListValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"),
        object_value=Literal("other", datatype=XSD.string),
        list_name=Literal("onlyList", datatype=XSD.string),
    )


@pytest.fixture
def list_value_wrong_list() -> ListValueRDF:
    return ListValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"),
        object_value=Literal("n1", datatype=XSD.string),
        list_name=Literal("other", datatype=XSD.string),
    )


@pytest.fixture
def text_richtext_value_corr() -> RichtextRDF:
    return RichtextRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"), Literal("Text", datatype=XSD.string)
    )


@pytest.fixture
def text_richtext_value_empty() -> RichtextRDF:
    return RichtextRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def text_simpletext_value_corr() -> SimpleTextRDF:
    return SimpleTextRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea"), Literal("Text", datatype=XSD.string)
    )


@pytest.fixture
def time_value_corr() -> TimeValueRDF:
    return TimeValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"),
        Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp),
    )


@pytest.fixture
def time_value_empty() -> TimeValueRDF:
    return TimeValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def uri_value_corr() -> UriValueRDF:
    return UriValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"),
        Literal("https://dasch.swiss", datatype=XSD.anyURI),
    )


@pytest.fixture
def uri_value_empty() -> UriValueRDF:
    return UriValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"), Literal("", datatype=XSD.string)
    )


@pytest.fixture
def uri_value_wrong() -> UriValueRDF:
    return UriValueRDF(
        URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"), Literal("with space", datatype=XSD.anyURI)
    )
