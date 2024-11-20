import pytest
from lxml import etree
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import KNORA_API
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import _make_one_prop_graph

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
namespaces = {"onto": ONTO, "knora-api": KNORA_API}

PERMISSION_LITERAL = Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)


@pytest.fixture
def permissions_lookup() -> dict[str, Permissions]:
    return {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}


@pytest.fixture
def lookups(permissions_lookup: dict[str, Permissions]) -> Lookups:
    return Lookups(
        project_iri="http://rdfh.ch/9999/project",
        id_to_iri=IriResolver({"one": "1"}),
        permissions=permissions_lookup,
        listnodes={"node": "http://rdfh.ch/9999/node"},
        namespaces=namespaces,
        jsonld_context=JSONLDContext({}),
    )


@pytest.fixture
def res_info() -> tuple[BNode, str]:
    return BNode(), "restype"


class TestMakeOnePropGraph:
    def test_boolean_success(self, lookups: Lookups, res_info: tuple[BNode, str]) -> None:
        res_bn, res_type = res_info
        xml_prop = etree.fromstring("""
        <boolean-prop name=":isTrueOrFalse">
            <boolean permissions="open">true</boolean>
        </boolean-prop>
        """)
        prop = XMLProperty.from_node(xml_prop, "boolean", "onto")
        result, prop_name = _make_one_prop_graph(prop, res_type, res_bn, lookups)
        assert len(result) == 4
        assert prop_name == ONTO.isTrueOrFalse
        val_bn = next(result.objects(res_bn, prop_name))
        rdf_type = next(result.objects(val_bn, RDF.type))
        assert rdf_type == KNORA_API.BooleanValue
        value = next(result.objects(val_bn, KNORA_API.booleanValueAsBoolean))
        assert value == Literal(True, datatype=XSD.boolean)
        permissions = next(result.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == PERMISSION_LITERAL
