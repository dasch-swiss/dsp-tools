from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.constants import IIIF_URI_VALUE
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.utils.rdflib_constants import KNORA_API


def make_iiif_uri_value_graph(iiif_uri: AbstractFileValue, res_node: BNode | URIRef) -> Graph:
    """
    Creates a graph with the IIIF-URI Link

    Args:
        iiif_uri: Information about the IIIF URI
        res_node: Node of the resource

    Returns:
        Graph with the IIIF-URI Value
    """
    return _make_abstract_file_value_graph(
        iiif_uri, IIIF_URI_VALUE, res_node, KNORA_API.stillImageFileValueHasExternalUrl
    )


def make_file_value_graph(
    bitstream_info: BitstreamInfo,
    rdf_prop_type_info: RDFPropTypeInfo,
    file_value_metadata: FileValueMetadata,
    res_node: BNode | URIRef,
) -> Graph:
    """
    Creates a graph with the File Value information.

    Args:
        bitstream_info: Information about the previously uploaded file
        rdf_prop_type_info: the type of value based on the extension
        file_value_metadata: Metadata of the file value
        res_node: Node of the resource

    Returns:
        Graph with the File Value
    """
    internal_filename = bitstream_info.internal_file_name
    file_value = AbstractFileValue(internal_filename, file_value_metadata)
    return _make_abstract_file_value_graph(file_value, rdf_prop_type_info, res_node)


def _make_abstract_file_value_graph(
    file_value: AbstractFileValue,
    type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
    has_file_name_prop: URIRef = KNORA_API.fileValueHasFilename,
) -> Graph:
    file_bn = BNode()
    g = _add_metadata(file_bn, file_value.metadata)
    g.add((res_node, type_info.knora_prop, file_bn))
    g.add((file_bn, RDF.type, type_info.knora_type))
    g.add((file_bn, has_file_name_prop, Literal(file_value.value, datatype=XSD.string)))
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
