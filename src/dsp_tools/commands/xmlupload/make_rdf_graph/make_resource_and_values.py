from typing import cast

from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.constants import FILE_TYPE_TO_RDF_MAPPER
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_abstract_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileIIIFUri
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFilePlaceholder
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.utils.rdf_constants import KNORA_API


def create_resource_with_values(
    resource: ProcessedResource,
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
    resource: ProcessedResource,
    res_node: BNode | URIRef,
    bitstream_information: BitstreamInfo | None,
    lookups: IRILookups,
) -> Graph:
    properties_graph = make_values(resource.values, res_node, lookups)

    if file_found := resource.file_value:
        abstract_value = _get_abstract_file_value(file_found, bitstream_information)
        properties_graph += make_abstract_file_value_graph(
            file_value=abstract_value,
            res_node=res_node,
        )
    return properties_graph


def _get_abstract_file_value(
    file_val: ProcessedFileValue, bitstream_information: BitstreamInfo | None
) -> AbstractFileValue:
    metadata = _make_file_value_metadata(file_val.metadata)
    prop_to_filename = KNORA_API.fileValueHasFilename
    prop_type_info = FILE_TYPE_TO_RDF_MAPPER[file_val.value_type]

    match file_val.value:
        case ProcessedFileIIIFUri():
            file_value_string = file_val.value.value
            prop_to_filename = KNORA_API.stillImageFileValueHasExternalUrl

        case ProcessedFileBitstream():
            bitstream = cast(BitstreamInfo, bitstream_information)
            file_value_string = bitstream.internal_file_name

        case ProcessedFilePlaceholder():
            file_value_string = file_val.value.value

        case _:
            raise UnreachableCodeError()

    return AbstractFileValue(
        value=file_value_string, metadata=metadata, prop_to_filename=prop_to_filename, prop_type_info=prop_type_info
    )


def _make_file_value_metadata(processed_metadata: ProcessedFileMetadata) -> FileValueMetadata:
    permissions = None
    if found := processed_metadata.permissions:
        permissions = str(found)
    return FileValueMetadata(
        processed_metadata.license_iri,
        processed_metadata.copyright_holder,
        processed_metadata.authorships,
        permissions,
    )


def _make_resource(resource: ProcessedResource, res_node: BNode | URIRef, project_iri: URIRef) -> Graph:
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
