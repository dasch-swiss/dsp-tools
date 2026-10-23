import base64
import dataclasses
import json
import re
from collections.abc import Iterator
from collections.abc import Set
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.ingest import BulkIngestedAssetClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.xmlupload.exceptions import XmlInputConversionError
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_abstract_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileIIIFUri
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeolocation
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeometry
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValue
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _get_one_processed_value
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _get_one_resource
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _resolve_permission
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _resolve_value_order
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_parsed_resources_and_mappers
from dsp_tools.utils.data_formats.geolocation_util import compose_geolocation_literal
from dsp_tools.utils.rdf_constants import KNORA_API
from dsp_tools.utils.rdf_constants import URN_DASCH_PLACEHOLDER
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedGeolocation
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file

_NON_IRI_CHARACTERS = re.compile(r"[^A-Za-z0-9_-]")
_LEGAL_INFO_PROPERTIES = (KNORA_API.hasLicense, KNORA_API.hasCopyrightHolder, KNORA_API.hasAuthorship)


def serialise_bulk_payload(
    xml_file: Path,
    creds: ServerCredentials,
    output_file: Path,
    lenient: bool = False,
    skip_ingested_files: bool = False,
    skip_resource_ids: Set[str] = frozenset(),
) -> None:
    """
    Serialises all resources of an XML data file into one knora-api v2 JSON-LD array, as the bulk import expects it.
    All resource and value IRIs are minted in the client. Lists, permissions and the project IRI come from the server.
    The bitstream text is used as internal filename, as after an ingest with the mapping CSV.

    Args:
        xml_file: XML data file
        creds: credentials of the server that has the project
        output_file: JSON-LD file to write
        lenient: for test data only. Unknown list nodes, permissions, authorships and resource ids get placeholders,
            and values that the conversion rejects are kept raw, instead of raising an error.
        skip_ingested_files: leave out bitstreams and placeholder files, for a server without the ingested assets
        skip_resource_ids: resources to leave out
    """
    root = parse_and_clean_xml_file(xml_file)
    shortcode = root.attrib["shortcode"]
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    project_iri = ProjectClientLive(creds.server, auth).get_project_iri(shortcode)
    clients = UploadClients(
        asset_client=BulkIngestedAssetClient(),
        list_client=ListGetClientLive(auth.server, shortcode),
        legal_info_client=LegalInfoClientLive(creds.server, shortcode, auth),
    )
    parsed_resources, lookups = get_parsed_resources_and_mappers(root, clients)
    if lenient:
        parsed_resources, lookups = make_lookups_lenient(parsed_resources, lookups, shortcode)
        processed = process_resources_lenient(parsed_resources, lookups)
    else:
        processed = get_processed_resources(parsed_resources, lookups, is_on_prod_like_server=False)
    nodes = serialise_resources(
        processed, URIRef(project_iri), shortcode, lenient, skip_ingested_files, skip_resource_ids
    )
    write_json_array(nodes, output_file)


@dataclass(kw_only=True)
class LenientIriResolver(IriResolver):
    """Mints a resource IRI for an unknown id. The IRI belongs to no resource, thus the link target does not exist."""

    shortcode: str

    def get(self, internal_id: str) -> str | None:
        if internal_id not in self.lookup:
            self.lookup[internal_id] = mint_resource_iri(self.shortcode)
        return self.lookup[internal_id]


def serialise_resources(
    resources: list[ProcessedResource],
    project_iri: URIRef,
    shortcode: str,
    lenient: bool,
    skip_ingested_files: bool = False,
    skip_resource_ids: Set[str] = frozenset(),
) -> Iterator[dict[str, Any]]:
    """
    Yields the expanded JSON-LD node objects of all resources and their values.
    With skip_ingested_files, bitstreams and placeholder files are left out. IIIF URIs stay.
    The resources in skip_resource_ids are left out.
    """
    resources = [res for res in resources if res.res_id not in skip_resource_ids]
    if skip_ingested_files:
        resources = [_without_ingested_file(res) for res in resources]
    minted, resolver = mint_resource_iris(resources, shortcode)
    if lenient:
        resolver = LenientIriResolver(lookup=resolver.lookup, shortcode=shortcode)
    lookups = IRILookups(project_iri=project_iri, id_to_iri=resolver)
    for res in minted:
        res_iri = URIRef(_get_iri(res))
        if lenient and res.file_value and res.file_value.value_type is None:
            graph = create_resource_with_values(dataclasses.replace(res, file_value=None), None, lookups)
            graph += _make_file_value_of_unknown_type(res.file_value, res_iri)
        else:
            graph = create_resource_with_values(res, _get_bitstream_info(res), lookups)
        if lenient:
            graph = _remove_placeholder_legal_info(graph)
        yield from json.loads(replace_blank_nodes(graph, res_iri).serialize(format="json-ld"))


def _without_ingested_file(resource: ProcessedResource) -> ProcessedResource:
    if resource.file_value is None or isinstance(resource.file_value.value, ProcessedFileIIIFUri):
        return resource
    return dataclasses.replace(resource, file_value=None)


def _remove_placeholder_legal_info(graph: Graph) -> Graph:
    """The server cannot parse the placeholder that xmlupload uses for missing legal info on test servers."""
    for prop in _LEGAL_INFO_PROPERTIES:
        for placeholder in (URIRef(URN_DASCH_PLACEHOLDER), Literal(URN_DASCH_PLACEHOLDER, datatype=XSD.string)):
            graph.remove((None, prop, placeholder))
    return graph


def _make_file_value_of_unknown_type(file_value: ProcessedFileValue, res_iri: URIRef) -> Graph:
    """A file without a known file type gets the abstract knora-api:FileValue."""
    metadata = file_value.metadata
    abstract_value = AbstractFileValue(
        value=file_value.value.value or "",
        metadata=FileValueMetadata(
            license_iri=metadata.license_iri,
            copyright_holder=metadata.copyright_holder,
            authorships=metadata.authorships,
            permissions=str(metadata.permissions) if metadata.permissions else None,
        ),
        prop_to_filename=KNORA_API.fileValueHasFilename,
        prop_type_info=RDFPropTypeInfo(KNORA_API.FileValue, KNORA_API.hasFileValue),
    )
    return make_abstract_file_value_graph(abstract_value, BNode(), res_iri)


def _get_bitstream_info(resource: ProcessedResource) -> BitstreamInfo | None:
    file_value = resource.file_value
    if file_value is None or not isinstance(file_value.value, ProcessedFileBitstream):
        return None
    return BulkIngestedAssetClient().get_bitstream_info(file_value.value, file_value.metadata.permissions)


def _get_iri(resource: ProcessedResource) -> str:
    if resource.migration_metadata is None or resource.migration_metadata.iri_str is None:
        raise ValueError(f"Resource {resource.res_id} has no IRI")
    return resource.migration_metadata.iri_str


def mint_resource_iris(
    resources: list[ProcessedResource], shortcode: str
) -> tuple[list[ProcessedResource], IriResolver]:
    """Keeps an IRI or ARK from the XML. All other resources get a minted IRI."""
    minted = [_with_iri(res, shortcode) for res in resources]
    return minted, IriResolver(lookup={res.res_id: _get_iri(res) for res in minted})


def _with_iri(resource: ProcessedResource, shortcode: str) -> ProcessedResource:
    migration = resource.migration_metadata or MigrationMetadata(None, None)
    if migration.iri_str:
        return resource
    return dataclasses.replace(
        resource, migration_metadata=dataclasses.replace(migration, iri_str=mint_resource_iri(shortcode))
    )


def mint_resource_iri(shortcode: str) -> str:
    return f"http://rdfh.ch/{shortcode}/{_make_uuid()}"


def _make_uuid() -> str:
    return base64.urlsafe_b64encode(uuid4().bytes).decode().rstrip("=")


def replace_blank_nodes(graph: Graph, res_iri: URIRef) -> Graph:
    """Gives each blank node of a resource graph a value IRI of the form {resource IRI}/values/{UUID}."""
    value_iris: dict[BNode, URIRef] = {}

    def _replace(node: Any) -> Any:
        if not isinstance(node, BNode):
            return node
        if node not in value_iris:
            value_iris[node] = URIRef(f"{res_iri}/values/{_make_uuid()}")
        return value_iris[node]

    replaced = Graph()
    for s, p, o in graph:
        replaced.add((_replace(s), p, _replace(o)))
    return replaced


def process_resources_lenient(resources: list[ParsedResource], lookups: XmlReferenceLookups) -> list[ProcessedResource]:
    """
    For test data only: a value that the xmlupload conversion rejects is kept raw,
    so that the server validation sees it.
    """
    return [_process_resource_lenient(res, lookups) for res in resources]


def _process_resource_lenient(resource: ParsedResource, lookups: XmlReferenceLookups) -> ProcessedResource:
    convertible: list[ParsedValue] = []
    raw: list[ProcessedValue] = []
    for val in resource.values:
        try:
            _get_one_processed_value(val, lookups)
            convertible.append(val)
        except XmlInputConversionError:
            raw.append(_make_raw_value(val, lookups))
    processed = _get_one_resource(
        dataclasses.replace(resource, values=convertible), lookups, is_on_prod_like_server=False
    )
    return dataclasses.replace(processed, values=[*processed.values, *raw])


def _make_raw_value(value: ParsedValue, lookups: XmlReferenceLookups) -> ProcessedValue:
    permissions = _resolve_permission(value.permissions_id, lookups.permissions)
    order = _resolve_value_order(value.value_order, value.xml_value_order)
    match value.value_type:
        case KnoraValueType.GEOLOCATION_VALUE if isinstance(value.value, ParsedGeolocation):
            return ProcessedGeolocation(
                _raw_geolocation(value.value), value.prop_name, value.comment, permissions, order
            )
        case KnoraValueType.GEOM_VALUE:
            return ProcessedGeometry(str(value.value or ""), value.prop_name, value.comment, permissions, order)
        case _:
            return ProcessedSimpleText(str(value.value or ""), value.prop_name, value.comment, permissions, order)


def _raw_geolocation(geolocation: ParsedGeolocation) -> str:
    try:
        return compose_geolocation_literal(geolocation.crs, geolocation.ordinates)
    except KeyError:
        ordinates = " ".join(f"{name}={number}" for name, number in geolocation.ordinates.items())
        return f"{geolocation.crs} {ordinates}"


def make_lookups_lenient(
    resources: list[ParsedResource], lookups: XmlReferenceLookups, shortcode: str
) -> tuple[list[ParsedResource], XmlReferenceLookups]:
    """
    For test data only: lets unresolvable references pass the processing, so that the server validation sees them.
    An unknown permissions id is removed. An unknown list node gets a placeholder IRI.
    An unknown authorship id becomes the author name.
    """
    lenient = XmlReferenceLookups(
        permissions=lookups.permissions,
        listnodes=dict(lookups.listnodes),
        authorships=dict(lookups.authorships),
    )
    for res in resources:
        _add_placeholders(res, lenient, shortcode)
    return [_remove_unknown_permissions(res, lenient) for res in resources], lenient


def _add_placeholders(resource: ParsedResource, lookups: XmlReferenceLookups, shortcode: str) -> None:
    authorship_ids = [resource.authorship_id]
    if resource.file_value:
        authorship_ids.append(resource.file_value.metadata.authorship_id)
    for authorship_id in authorship_ids:
        if authorship_id and authorship_id not in lookups.authorships:
            lookups.authorships[authorship_id] = [authorship_id]
    for val in resource.values:
        if val.value_type == KnoraValueType.LIST_VALUE and isinstance(val.value, tuple):
            list_name, node_name = val.value
            key = (list_name or "", node_name or "")
            if key not in lookups.listnodes:
                placeholder = _NON_IRI_CHARACTERS.sub("_", f"missing-{list_name}-{node_name}")
                lookups.listnodes[key] = f"http://rdfh.ch/lists/{shortcode}/{placeholder}"


def _remove_unknown_permissions(resource: ParsedResource, lookups: XmlReferenceLookups) -> ParsedResource:
    file_value = resource.file_value
    if file_value:
        metadata = file_value.metadata
        file_value = dataclasses.replace(
            file_value,
            metadata=dataclasses.replace(metadata, permissions_id=_known(metadata.permissions_id, lookups)),
        )
    return dataclasses.replace(
        resource,
        permissions_id=_known(resource.permissions_id, lookups),
        values=[_value_with_known_permissions(val, lookups) for val in resource.values],
        file_value=file_value,
    )


def _value_with_known_permissions(value: ParsedValue, lookups: XmlReferenceLookups) -> ParsedValue:
    return dataclasses.replace(value, permissions_id=_known(value.permissions_id, lookups))


def _known(permissions_id: str | None, lookups: XmlReferenceLookups) -> str | None:
    return permissions_id if permissions_id in lookups.permissions else None


def write_json_array(nodes: Iterator[dict[str, Any]], output_file: Path) -> None:
    """Writes the nodes one by one, so that the whole array never has to be in memory."""
    with output_file.open("w", encoding="utf-8") as f:
        f.write("[")
        for number, node in enumerate(nodes):
            f.write(",\n" if number else "\n")
            f.write(json.dumps(node, ensure_ascii=False))
        f.write("\n]\n")
