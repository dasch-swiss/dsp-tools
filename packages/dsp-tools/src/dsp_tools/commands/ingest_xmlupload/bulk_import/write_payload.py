import json
from pathlib import Path
from typing import Any
from typing import TextIO

from rdflib import RDF
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import make_value_iri
from dsp_tools.commands.ingest_xmlupload.exceptions import ResourceIriMissingError
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_json
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.utils.rdf_constants import KNORA_API


def write_payload_file(resources: list[ProcessedResource], lookups: IRILookups, target: Path) -> None:
    """
    Writes all resources as one JSON-LD file: a flat array of expanded node objects, without blank nodes.
    The IRI of every resource must already be in `lookups.id_to_iri`.

    Args:
        resources: the resources of the XML file
        lookups: lookups that contain the minted IRI of every resource
        target: path of the JSON-LD file

    Raises:
        ResourceIriMissingError: if a resource has no IRI
    """
    # The file is written to a `.part` file and renamed at the end, so that `target` never holds a partial payload.
    # Only one resource graph is held in memory at a time, because the payload can be larger than the memory.
    part_file = target.with_suffix(target.suffix + ".part")
    try:
        with part_file.open("w", encoding="utf-8") as file:
            _write_nodes(resources, lookups, file)
        part_file.replace(target)
    finally:
        part_file.unlink(missing_ok=True)


def _write_nodes(resources: list[ProcessedResource], lookups: IRILookups, file: TextIO) -> None:
    file.write("[")
    is_first = True
    for res in resources:
        for node in _make_resource_nodes(res, lookups):
            if not is_first:
                file.write(",")
            is_first = False
            json.dump(node, file, ensure_ascii=False)
    file.write("]")


def _make_resource_nodes(res: ProcessedResource, lookups: IRILookups) -> list[dict[str, Any]]:
    if not (res_iri := lookups.id_to_iri.get(res.res_id)):
        raise ResourceIriMissingError(res.res_id)
    graph = create_resource_with_values(
        res,
        _get_bitstream_info(res),
        lookups,
        res_node=URIRef(res_iri),
        make_value_node=lambda: URIRef(make_value_iri(res_iri)),
    )
    _add_file_value_order(graph)
    return serialise_json(graph)


def _get_bitstream_info(res: ProcessedResource) -> BitstreamInfo | None:
    if (file_value := res.file_value) and isinstance(file_value.value, ProcessedFileBitstream):
        return BitstreamInfo(file_value.value.value, file_value.metadata.permissions)
    return None


def _add_file_value_order(graph: Graph) -> None:
    # The bulk data import needs `valueHasOrder` on every value. The graph builders omit it on the file value.
    for node, value_type in list(graph.subject_objects(RDF.type)):
        if str(value_type).endswith("FileValue") and graph.value(node, KNORA_API.valueHasOrder) is None:
            graph.add((node, KNORA_API.valueHasOrder, Literal(0, datatype=XSD.integer)))
