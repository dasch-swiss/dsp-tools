from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.utils.rdf_constants import KNORA_API


def make_abstract_file_value_graph(
    file_value: AbstractFileValue,
    res_node: BNode | URIRef,
) -> Graph:
    file_bn = BNode()
    g = _add_metadata(file_bn, file_value.metadata)
    g.add((res_node, file_value.prop_type_info.knora_prop, file_bn))
    g.add((file_bn, RDF.type, file_value.prop_type_info.knora_type))
    g.add((file_bn, file_value.prop_to_filename, Literal(file_value.value, datatype=XSD.string)))
    return g


def _add_metadata(file_bn: BNode, metadata: FileValueMetadata) -> Graph:
    g = Graph()
    g.add((file_bn, KNORA_API.hasLicense, URIRef(metadata.license_iri)))
    g.add((file_bn, KNORA_API.hasCopyrightHolder, Literal(metadata.copyright_holder, datatype=XSD.string)))
    for auth in metadata.authorships:
        g.add((file_bn, KNORA_API.hasAuthorship, Literal(auth, datatype=XSD.string)))
    if metadata.permissions:
        g.add((file_bn, KNORA_API.hasPermissions, Literal(metadata.permissions, datatype=XSD.string)))
    return g
