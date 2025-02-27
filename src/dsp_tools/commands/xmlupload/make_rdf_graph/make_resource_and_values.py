from typing import cast

from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.constants import KNORA_API
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileMetadata
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata


def create_resource_with_values(
    resource: IntermediaryResource,
    bitstream_information: BitstreamInfo | None,
    lookups: IRILookups,
) -> Graph:
    """
    This function takes an XMLResource and serialises it into a json-ld type dict that can be sent to the API.

    Args:
        resource: XMLResource
        bitstream_information: if the resource has a FileValue
        lookups: Lookups to resolve IRIs, etc.

    Returns:
        A resource as a graph
    """

    graph = Graph()

    res_node: BNode | URIRef = BNode()
    if migration := resource.migration_metadata:
        if migration.iri_str:
            res_node = URIRef(migration.iri_str)
        graph += _make_migration_metadata(migration, res_node)

    graph += _make_resource(resource=resource, res_node=res_node, project_iri=lookups.project_iri)

    graph += _make_values_graph_from_resource(
        resource=resource, res_node=res_node, bitstream_information=bitstream_information, lookups=lookups
    )

    return graph


def _make_values_graph_from_resource(
    resource: IntermediaryResource,
    res_node: BNode | URIRef,
    bitstream_information: BitstreamInfo | None,
    lookups: IRILookups,
) -> Graph:
    properties_graph = make_values(resource.values, res_node, lookups)

    if resource.iiif_uri:
        metadata = _make_file_value_metadata(resource.iiif_uri.metadata)
        iiif_g = make_iiif_uri_value_graph(AbstractFileValue(resource.iiif_uri.value, metadata), res_node)
        properties_graph += iiif_g

    elif bitstream_information:
        file_val = cast(IntermediaryFileValue, resource.file_value)
        metadata = _make_file_value_metadata(file_val.metadata)
        file_g = make_file_value_graph(bitstream_information, metadata, res_node)
        properties_graph += file_g

    return properties_graph


def _make_file_value_metadata(intermediary_metadata: IntermediaryFileMetadata) -> FileValueMetadata:
    permissions = None
    if found := intermediary_metadata.permissions:
        permissions = str(found)
    return FileValueMetadata(
        intermediary_metadata.license_iri,
        intermediary_metadata.copyright_holder,
        intermediary_metadata.authorships,
        permissions,
    )


def _make_resource(resource: IntermediaryResource, res_node: BNode | URIRef, project_iri: URIRef) -> Graph:
    g = Graph()
    g.add((res_node, RDF.type, URIRef(resource.type_iri)))
    g.add((res_node, RDFS.label, Literal(resource.label, datatype=XSD.string)))
    g.add((res_node, KNORA_API.attachedToProject, project_iri))
    if resource.permissions:
        g.add((res_node, KNORA_API.hasPermissions, Literal(str(resource.permissions), datatype=XSD.string)))
    return g


def _make_migration_metadata(migration_metadata: MigrationMetadata, res_node: BNode | URIRef) -> Graph:
    g = Graph()
    if date := migration_metadata.creation_date:
        g.add((res_node, KNORA_API.creationDate, Literal(str(date), datatype=XSD.dateTimeStamp)))
    return g
