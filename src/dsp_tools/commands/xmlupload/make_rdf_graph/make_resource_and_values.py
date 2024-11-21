from typing import Any

from rdflib import BNode

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.make_rdf_graph.helpers import resolve_permission
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import _make_bitstream_file_value
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_values
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import Lookups
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
    res_bnode = BNode()
    res = _make_resource(resource=resource, bitstream_information=bitstream_information, lookup=lookup)
    vals = make_values(resource, res_bnode, lookup)
    res.update(vals)
    res.update(lookup.jsonld_context.serialise())
    return res


def _make_resource(
    resource: XMLResource, bitstream_information: BitstreamInfo | None, lookup: Lookups
) -> dict[str, Any]:
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
    res = serialise_resource.serialise()
    if bitstream_information:
        res.update(_make_bitstream_file_value(bitstream_information))
    return res
