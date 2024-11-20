from lxml import etree
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.transform_resource_and_values_for_upload import KNORA_API

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")


def test_make_boolean_value_with_permissions() -> None:
    permissions_lookup = {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}
    xml_str = """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <boolean-prop name=":isTrueOrFalse">
                <boolean permissions="open">true</boolean>
            </boolean-prop>
        </resource>
        """
    xmlresource = XMLResource.from_node(etree.fromstring(xml_str), "foo")
    test_val: XMLValue = xmlresource.properties[0].values[0]
    res_bn = BNode()
    prop_name = ONTO.isTrueOrFalse
    bool_graph = Graph()
    number_of_triples = 4
    assert len(bool_graph) == number_of_triples
    value_bn = next(bool_graph.objects(res_bn, prop_name))
    rdf_type = next(bool_graph.objects(value_bn, RDF.type))
    assert rdf_type == KNORA_API.BooleanValue
    bool_val = next(bool_graph.objects(value_bn, KNORA_API.booleanValueAsBoolean))
    assert bool_val == Literal(True)
    permissions = next(bool_graph.objects(value_bn, KNORA_API.hasPermissions))
    assert permissions == Literal(str(permissions_lookup.get("open")))
