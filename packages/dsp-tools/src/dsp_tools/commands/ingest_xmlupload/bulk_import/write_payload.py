import json
from pathlib import Path
from typing import Any
from typing import TextIO

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import make_value_iri
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import FILE_TYPE_TO_RDF_MAPPER
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_json
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.utils.rdf_constants import KNORA_API

_FILE_VALUE_CLASSES = frozenset(info.knora_type for info in FILE_TYPE_TO_RDF_MAPPER.values())


def write_payload_file(resources: list[ProcessedResource], lookups: IRILookups, target: Path) -> None:
    """
    Writes all resources as one JSON-LD file: a flat array of expanded node objects, without blank nodes.
    The IRI of every resource must already be in `lookups.id_to_iri`.

    Args:
        resources: the resources of the XML file
        lookups: lookups that contain the minted IRI of every resource
        target: path of the JSON-LD file
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
    nodes = (node for res in resources for node in _make_resource_nodes(res, lookups))
    file.write("[")
    for index, node in enumerate(nodes):
        if index > 0:
            file.write(",")
        json.dump(node, file, ensure_ascii=False)
    file.write("]")


def _make_resource_nodes(res: ProcessedResource, lookups: IRILookups) -> list[dict[str, Any]]:
    res_iri = lookups.id_to_iri.lookup[res.res_id]
    graph = create_resource_with_values(
        res,
        _get_bitstream_info(res),
        lookups,
        res_node=URIRef(res_iri),
        make_value_node=_make_value_node,
    )
    _add_file_value_order(graph)
    return serialise_json(graph)


def _make_value_node(res_node: BNode | URIRef) -> URIRef:
    return URIRef(make_value_iri(str(res_node)))


def _get_bitstream_info(res: ProcessedResource) -> BitstreamInfo | None:
    if (file_value := res.file_value) and isinstance(file_value.value, ProcessedFileBitstream):
        return BitstreamInfo(file_value.value.value, file_value.metadata.permissions)
    return None


def _add_file_value_order(graph: Graph) -> None:
    # The bulk data import needs `valueHasOrder` on every value. The graph builders do not set it on the file value,
    # because xmlupload must not send it.
    file_nodes = [node for node, value_type in graph.subject_objects(RDF.type) if value_type in _FILE_VALUE_CLASSES]
    for node in file_nodes:
        graph.add((node, KNORA_API.valueHasOrder, Literal(0, datatype=XSD.integer)))
