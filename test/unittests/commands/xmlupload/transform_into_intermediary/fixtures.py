import pytest

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLFileMetadata
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.datetimestamp import DateTimeStamp


@pytest.fixture
def lookups() -> IntermediaryLookups:
    return IntermediaryLookups(
        permissions={"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})},
        listnodes={"list:node": "http://rdfh.ch/9999/node"},
        namespaces={
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "onto": "http://0.0.0.0:3333/ontology/9999/onto/v2#",
        },
        authorships={"auth_id": ["author"]},
    )


@pytest.fixture
def bool_prop() -> XMLProperty:
    return XMLProperty(name="onto:boolProp", valtype="boolean", values=[XMLValue(value="true")])


@pytest.fixture
def bool_prop_with_permissions() -> XMLProperty:
    return XMLProperty(name="onto:boolProp", valtype="boolean", values=[XMLValue(value="true", permissions="open")])


@pytest.fixture
def bool_prop_with_non_existing_permissions() -> XMLProperty:
    return XMLProperty(
        name="onto:boolProp", valtype="boolean", values=[XMLValue(value="true", permissions="nonExisting")]
    )


@pytest.fixture
def bool_prop_with_comment() -> XMLProperty:
    return XMLProperty(name="onto:boolProp", valtype="boolean", values=[XMLValue(value="true", comment="comment")])


@pytest.fixture
def color_prop() -> XMLProperty:
    return XMLProperty(name="onto:colorProp", valtype="color", values=[XMLValue("#5d1f1e")])


@pytest.fixture
def date_prop() -> XMLProperty:
    return XMLProperty(name="onto:dateProp", valtype="date", values=[XMLValue("CE:1849:CE:1850")])


@pytest.fixture
def decimal_prop() -> XMLProperty:
    return XMLProperty(name="onto:decimalProp", valtype="decimal", values=[XMLValue("1.4")])


@pytest.fixture
def decimal_prop_with_two_values() -> XMLProperty:
    return XMLProperty(name="onto:decimalProp", valtype="decimal", values=[XMLValue("1.0"), XMLValue("2.0")])


@pytest.fixture
def simple_text_prop() -> XMLProperty:
    return XMLProperty(name="onto:simpleTextProp", valtype="text", values=[XMLValue(value="text")])


@pytest.fixture
def richtext_prop() -> XMLProperty:
    return XMLProperty(
        name="onto:richTextProp",
        valtype="text",
        values=[XMLValue(FormattedTextValue("<text>this is text</text>"), resrefs={"id"})],
    )


@pytest.fixture
def geoname_prop() -> XMLProperty:
    return XMLProperty(name="onto:geonameProp", valtype="geoname", values=[XMLValue("5416656")])


@pytest.fixture
def integer_prop() -> XMLProperty:
    return XMLProperty(name="onto:integerProp", valtype="integer", values=[XMLValue("1")])


@pytest.fixture
def list_prop() -> XMLProperty:
    return XMLProperty(name="onto:listProp", valtype="list", values=[XMLValue("list:node")])


@pytest.fixture
def resptr_prop() -> XMLProperty:
    return XMLProperty(name="onto:linkProp", valtype="resptr", values=[XMLValue("other_id")])


@pytest.fixture
def time_prop() -> XMLProperty:
    return XMLProperty(name="onto:timeProp", valtype="time", values=[XMLValue("2019-10-23T13:45:12.01-14:00")])


@pytest.fixture
def uri_prop() -> XMLProperty:
    return XMLProperty(name="onto:uriProp", valtype="uri", values=[XMLValue("https://dasch.swiss")])


@pytest.fixture
def iiif_uri() -> IIIFUriInfo:
    return IIIFUriInfo(
        "https://this/is/a/uri.jpg",
        XMLFileMetadata(
            license_="http://rdfh.ch/licenses/cc-by-nc-4.0", copyright_holder="copy", authorship_id="auth_id"
        ),
    )


@pytest.fixture
def bitstream() -> XMLBitstream:
    return XMLBitstream(
        "file.jpg",
        XMLFileMetadata(
            license_="http://rdfh.ch/licenses/cc-by-nc-4.0", copyright_holder="copy", authorship_id="auth_id"
        ),
    )


@pytest.fixture
def iiif_uri_with_permission() -> IIIFUriInfo:
    return IIIFUriInfo(
        "https://this/is/a/uri.jpg",
        XMLFileMetadata(
            license_="http://rdfh.ch/licenses/cc-by-nc-4.0",
            copyright_holder="copy",
            authorship_id="auth_id",
            permissions="open",
        ),
    )


@pytest.fixture
def bitstream_with_permission() -> XMLBitstream:
    return XMLBitstream(
        "file.jpg",
        XMLFileMetadata(
            license_="http://rdfh.ch/licenses/cc-by-nc-4.0",
            copyright_holder="copy",
            authorship_id="auth_id",
            permissions="open",
        ),
    )


@pytest.fixture
def resource_one_prop(bool_prop: XMLProperty) -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=None,
        bitstream=None,
        iiif_uri=None,
        properties=[bool_prop],
    )


@pytest.fixture
def resource_with_permissions() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions="open",
        creation_date=None,
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )


@pytest.fixture
def resource_with_iiif_uri(iiif_uri: IIIFUriInfo) -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=None,
        bitstream=None,
        iiif_uri=iiif_uri,
        properties=[],
    )


@pytest.fixture
def resource_with_bitstream(bitstream: XMLBitstream) -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=None,
        bitstream=bitstream,
        iiif_uri=None,
        properties=[],
    )


@pytest.fixture
def resource_with_unknown_permissions() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions="nonExisting",
        creation_date=None,
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )


@pytest.fixture
def resource_with_ark() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri=None,
        ark="ark:/72163/4123-43xc6ivb931-a.2022829",
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=DateTimeStamp("1999-12-31T23:59:59.9999999+01:00"),
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )


@pytest.fixture
def resource_with_iri() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
        ark=None,
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=None,
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )


@pytest.fixture
def resource_with_ark_and_iri() -> XMLResource:
    return XMLResource(
        res_id="id",
        iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
        ark="ark:/72163/4123-43xc6ivb931-a.2022829",
        label="lbl",
        restype="onto:ResourceType",
        permissions=None,
        creation_date=DateTimeStamp("1999-12-31T23:59:59.9999999+01:00"),
        bitstream=None,
        iiif_uri=None,
        properties=[],
    )
