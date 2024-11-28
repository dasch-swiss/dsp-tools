import pytest

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup


@pytest.fixture
def lookups() -> IntermediaryLookup:
    return IntermediaryLookup(
        permissions={},
        listnodes={},
        namespaces={"knora-api": "", "onto": ""},
    )


@pytest.fixture
def value_with_string() -> XMLValue:
    return XMLValue(value="true")


@pytest.fixture
def value_with_string_and_comment() -> XMLValue:
    return XMLValue(value="true", comment="comment")


@pytest.fixture
def value_with_string_and_permissions() -> XMLValue:
    return XMLValue(value="true", permissions="open")


@pytest.fixture
def bool_prop(value_with_string) -> XMLProperty:
    return XMLProperty(name=":boolProp", valtype="bool", values=[value_with_string])


@pytest.fixture
def color_prop() -> XMLProperty:
    return XMLProperty(name=":colorProp", valtype="color", values=[XMLValue("#5d1f1e")])


@pytest.fixture
def date_prop() -> XMLProperty:
    return XMLProperty(name=":dateProp", valtype="date", values=[XMLValue("CE:1849:CE:1850")])


@pytest.fixture
def decimal_prop() -> XMLProperty:
    return XMLProperty(name=":decimalProp", valtype="decimal", values=[XMLValue("1.4")])


@pytest.fixture
def simple_text_prop(value_with_string) -> XMLProperty:
    return XMLProperty(name=":simpleTextProp", valtype="text", values=[value_with_string])


@pytest.fixture
def richtext_prop(value_with_string) -> XMLProperty:  # TODO
    return XMLProperty(name=":richTextProp", valtype="text", values=[value_with_string])


@pytest.fixture
def geoname_prop() -> XMLProperty:
    return XMLProperty(name=":geonameProp", valtype="geoname", values=[XMLValue("5416656")])


@pytest.fixture
def integer_prop() -> XMLProperty:
    return XMLProperty(name=":integerProp", valtype="integer", values=[XMLValue("1")])


@pytest.fixture
def list_prop() -> XMLProperty:
    return XMLProperty(name=":listProp", valtype="list", values=[XMLValue("list:node")])


@pytest.fixture
def resptr_prop(value_with_string) -> XMLProperty:
    return XMLProperty(name=":linkProp", valtype="resptr", values=[value_with_string])


@pytest.fixture
def time_prop() -> XMLProperty:
    return XMLProperty(name=":timeProp", valtype="time", values=[XMLValue("2019-10-23T13:45:12.01-14:00")])


@pytest.fixture
def uri_prop() -> XMLProperty:
    return XMLProperty(name=":uriProp", valtype="uri", values=[XMLValue("https://dasch.swiss")])


@pytest.fixture
def resource() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype=":ResourceType",
        permissions=None,
        creation_date=None,
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )
