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
    val_node: BNode,
    res_node: BNode | URIRef,
) -> Graph:
    g = _add_metadata(val_node, file_value.metadata)
    g.add((res_node, file_value.prop_type_info.knora_prop, val_node))
    g.add((val_node, RDF.type, file_value.prop_type_info.knora_type))
    g.add((val_node, file_value.prop_to_filename, Literal(file_value.value, datatype=XSD.string)))
    return g


def _add_metadata(val_node: BNode, metadata: FileValueMetadata) -> Graph:
    g = Graph()
    g.add((val_node, KNORA_API.hasLicense, URIRef(metadata.license_iri)))
    g.add((val_node, KNORA_API.hasCopyrightHolder, Literal(metadata.copyright_holder, datatype=XSD.string)))
    for auth in metadata.authorships:
        g.add((val_node, KNORA_API.hasAuthorship, Literal(auth, datatype=XSD.string)))
    if metadata.permissions:
        g.add((val_node, KNORA_API.hasPermissions, Literal(metadata.permissions, datatype=XSD.string)))
    return g
