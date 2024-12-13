from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from unittests.commands.validate_data.constants import KNORA_API

from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.commands.xmlupload.models.serialise_resource import SerialiseMigrationMetadata
from dsp_tools.commands.xmlupload.models.serialise_resource import SerialiseResource


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

    graph += _make_resource(resource=resource, res_node=res_node, lookup=lookups)

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
        permissions = None
        if found := resource.iiif_uri.metadata.permissions:
            permissions = str(found)
        metadata = FileValueMetadata(permissions)
        iiif_val = AbstractFileValue(resource.iiif_uri.value, metadata)
        iiif_g = make_iiif_uri_value_graph(iiif_val, res_node)
        properties_graph += iiif_g

    elif bitstream_information:
        file_g = make_file_value_graph(bitstream_information, res_node)
        properties_graph += file_g

    return properties_graph


def _make_resource(resource: IntermediaryResource, res_node: BNode | URIRef, lookup: IRILookups) -> Graph:
    migration_metadata = None
    if resource.migration_metadata:
        migration_metadata = SerialiseMigrationMetadata(
            iri=resource.migration_metadata.iri_str,
            creation_date=resource.migration_metadata.creation_date,
        )
    permissions = None
    if resource.permissions:
        permissions = str(resource.permissions)
    serialise_resource = SerialiseResource(
        res_id=resource.res_id,
        res_type=resource.type_iri,
        label=resource.label,
        permissions=permissions,
        project_iri=lookup.project_iri,
        migration_metadata=migration_metadata,
    )
    return serialise_resource.serialise()


def _make_migration_metadata(migration_metadata: MigrationMetadata, res_node: BNode | URIRef) -> Graph:
    g = Graph()
    if date := migration_metadata.creation_date:
        g.add((res_node, KNORA_API.creationDate, Literal(str(date), datatype=XSD.dateTimeStamp)))
    return g
