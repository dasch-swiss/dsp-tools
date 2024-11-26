from typing import Any

from rdflib import BNode

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.make_rdf_graph.helpers import resolve_permission
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_serialiser import serialise_property_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.commands.xmlupload.models.serialise_resource import SerialiseMigrationMetadata
from dsp_tools.commands.xmlupload.models.serialise_resource import SerialiseResource


def create_resource_with_values(
    resource: XMLResource, bitstream_information: BitstreamInfo | None, lookup: Lookups
) -> dict[str, Any]:
    """
    This function takes an XMLResource and serialises it into a json-ld type dict that can be sent to the API.

    Args:
        resource: XMLResource
        bitstream_information: if the resource has a FileValue
        lookup: Lookups to resolve IRIs, etc.

    Returns:
        A resource serialised in json-ld type format.
    """

    res = _make_resource(resource=resource, lookup=lookup)
    res.update(_make_values_dict_from_resource(resource, bitstream_information, lookup))
    res.update(lookup.jsonld_context.serialise())
    return res


def _make_values_dict_from_resource(
    resource: XMLResource, bitstream_information: BitstreamInfo | None, lookups: Lookups
) -> dict[str, Any]:
    res_bnode = BNode()

    properties_graph, last_prop_name = make_values(resource.properties, resource.restype, res_bnode, lookups)

    if resource.iiif_uri:
        resolved_permissions = resolve_permission(resource.iiif_uri.permissions, lookups.permissions)
        metadata = FileValueMetadata(resolved_permissions)
        iiif_val = AbstractFileValue(resource.iiif_uri.value, metadata)
        iiif_g, last_prop_name = make_iiif_uri_value_graph(iiif_val, res_bnode)
        properties_graph += iiif_g

    elif bitstream_information:
        file_g, last_prop_name = make_file_value_graph(bitstream_information, res_bnode)
        properties_graph += file_g

    if last_prop_name:
        return serialise_property_graph(properties_graph, last_prop_name)
    return {}  # we allow resources without properties


def _make_resource(resource: XMLResource, lookup: Lookups) -> dict[str, Any]:
    migration_metadata = None
    res_iri = resource.iri
    creation_date = resource.creation_date
    if resource.ark:
        res_iri = convert_ark_v0_to_resource_iri(resource.ark)
    if any([creation_date, res_iri]):
        migration_metadata = SerialiseMigrationMetadata(iri=res_iri, creation_date=resource.creation_date)
    resolved_permission = resolve_permission(resource.permissions, lookup.permissions)
    serialise_resource = SerialiseResource(
        res_id=resource.res_id,
        res_type=resource.restype,
        label=resource.label,
        permissions=resolved_permission,
        project_iri=lookup.project_iri,
        migration_metadata=migration_metadata,
    )
    return serialise_resource.serialise()
