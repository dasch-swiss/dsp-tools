import pytest
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
from test.unittests.commands.validate_data.constants import ONTO


@pytest.fixture
def rdf_resource() -> ResourceRDF:
    return ResourceRDF(
        res_iri=URIRef("id"), res_class=ONTO.ClassWithEverything, label=Literal("lbl", datatype=XSD.string)
    )


@pytest.fixture
def rdf_boolean_value_corr() -> BooleanValueRDF:
    return BooleanValueRDF(ONTO.testBoolean, Literal("false", datatype=XSD.boolean), URIRef("id"))


@pytest.fixture
def rdf_boolean_value_empty() -> BooleanValueRDF:
    return BooleanValueRDF(ONTO.testBoolean, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_color_value_corr() -> ColorValueRDF:
    return ColorValueRDF(ONTO.testColor, Literal("00ff00", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_date_value_corr() -> DateValueRDF:
    return DateValueRDF(
        ONTO.testSubDate1,
        Literal("JULIAN:BCE:0700:BCE:0600", datatype=XSD.string),
        URIRef("id"),
    )


@pytest.fixture
def rdf_decimal_value_corr() -> DecimalValueRDF:
    return DecimalValueRDF(ONTO.testDecimalSimpleText, Literal("1.2", datatype=XSD.decimal), URIRef("id"))


@pytest.fixture
def rdf_decimal_value_empty() -> DecimalValueRDF:
    return DecimalValueRDF(ONTO.testDecimalSimpleText, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_geoname_value_corr() -> GeonameValueRDF:
    return GeonameValueRDF(ONTO.testGeoname, Literal("1241345", datatype=XSD.integer), URIRef("id"))


@pytest.fixture
def rdf_integer_value_corr() -> IntValueRDF:
    return IntValueRDF(ONTO.testIntegerSimpleText, Literal("1", datatype=XSD.integer), URIRef("id"))


@pytest.fixture
def rdf_integer_value_empty() -> IntValueRDF:
    return IntValueRDF(ONTO.testIntegerSimpleText, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_link_value_corr() -> LinkValueRDF:
    return LinkValueRDF(ONTO.testHasLinkTo, URIRef("link-id"), URIRef("id"))


@pytest.fixture
def rdf_link_value_empty() -> LinkValueRDF:
    return LinkValueRDF(ONTO.testHasLinkTo, URIRef(""), URIRef("id"))


@pytest.fixture
def rdf_list_value_corr() -> ListValueRDF:
    return ListValueRDF(
        ONTO.testListProp,
        object_value=Literal("n1", datatype=XSD.string),
        list_name=Literal("firstList", datatype=XSD.string),
        res_iri=URIRef("id"),
    )


@pytest.fixture
def rdf_list_value_wrong_node() -> ListValueRDF:
    return ListValueRDF(
        ONTO.testListProp,
        object_value=Literal("other", datatype=XSD.string),
        list_name=Literal("firstList", datatype=XSD.string),
        res_iri=URIRef("id"),
    )


@pytest.fixture
def rdf_list_value_wrong_list() -> ListValueRDF:
    return ListValueRDF(
        ONTO.testListProp,
        object_value=Literal("n1", datatype=XSD.string),
        list_name=Literal("other", datatype=XSD.string),
        res_iri=URIRef("id"),
    )


@pytest.fixture
def rdf_text_richtext_value_corr() -> RichtextRDF:
    return RichtextRDF(ONTO.testRichtext, Literal("Text", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_text_richtext_value_empty() -> RichtextRDF:
    return RichtextRDF(ONTO.testRichtext, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_text_simpletext_value_corr() -> SimpleTextRDF:
    return SimpleTextRDF(ONTO.testTextarea, Literal("Text", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_time_value_corr() -> TimeValueRDF:
    return TimeValueRDF(
        ONTO.testTimeValue,
        Literal("2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp),
        URIRef("id"),
    )


@pytest.fixture
def rdf_time_value_empty() -> TimeValueRDF:
    return TimeValueRDF(ONTO.testTimeValue, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_uri_value_corr() -> UriValueRDF:
    return UriValueRDF(
        ONTO.testUriValue,
        Literal("https://dasch.swiss", datatype=XSD.anyURI),
        URIRef("id"),
    )


@pytest.fixture
def rdf_uri_value_empty() -> UriValueRDF:
    return UriValueRDF(ONTO.testUriValue, Literal("", datatype=XSD.string), URIRef("id"))


@pytest.fixture
def rdf_uri_value_wrong() -> UriValueRDF:
    return UriValueRDF(ONTO.testUriValue, Literal("with space", datatype=XSD.anyURI), URIRef("id"))
