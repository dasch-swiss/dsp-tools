import pytest

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup


@pytest.fixture
def lookups() -> IntermediaryLookup:
    return IntermediaryLookup()


@pytest.fixture
def value_with_true() -> XMLValue:
    return XMLValue(value="true")


@pytest.fixture
def value_with_true_and_comment() -> XMLValue:
    return XMLValue(value="true", comment="comment")


@pytest.fixture
def value_with_true_and_permissions() -> XMLValue:
    return XMLValue(value="true", permissions="open")


@pytest.fixture
def bool_prop(value_with_true) -> XMLProperty:
    return XMLProperty(name=":boolProp", valtype="bool", values=[value_with_true])


@pytest.fixture
def color_prop(value_with_true) -> XMLProperty:  # TODO: val
    return XMLProperty(name=":colorProp", valtype="color", values=[value_with_true])


@pytest.fixture
def date_prop(value_with_true) -> XMLProperty:  # TODO: val
    return XMLProperty(name=":dateProp", valtype="date", values=[value_with_true])


@pytest.fixture
def decimal_prop(value_with_true) -> XMLProperty:  # TODO: val
    return XMLProperty(name=":decimalProp", valtype="decimal", values=[value_with_true])


@pytest.fixture
def simple_text_prop(value_with_true) -> XMLProperty:  # TODO: val
    return XMLProperty(name=":simpleTextProp", valtype="text", values=[value_with_true])


@pytest.fixture
def richtext_prop(value_with_true) -> XMLProperty:
    return XMLProperty(name=":richTextProp", valtype="text", values=[value_with_true])


@pytest.fixture
def geoname_prop(value_with_true) -> XMLProperty:  # TODO: val
    return XMLProperty(name=":geonameProp", valtype="geoname", values=[value_with_true])


@pytest.fixture
def integer_prop(value_with_true) -> XMLProperty:  # TODO
    return XMLProperty(name=":integerProp", valtype="integer", values=[value_with_true])


@pytest.fixture
def list_prop(value_with_true) -> XMLProperty:  # TODO
    return XMLProperty(name=":listProp", valtype="list", values=[value_with_true])


@pytest.fixture
def resptr_prop(value_with_true) -> XMLProperty:  # TODO
    return XMLProperty(name=":linkProp", valtype="resptr", values=[value_with_true])


@pytest.fixture
def time_prop(value_with_true) -> XMLProperty:  # TODO
    return XMLProperty(name=":timeProp", valtype="time", values=[value_with_true])


@pytest.fixture
def uri_prop(value_with_true) -> XMLProperty:  # TODO
    return XMLProperty(name=":uriProp", valtype="uri", values=[value_with_true])


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
