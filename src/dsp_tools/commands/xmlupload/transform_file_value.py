from pathlib import Path

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import ARCHIVE_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import AUDIO_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import DOCUMENT_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import MOVING_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import STILL_IMAGE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import TEXT_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import AbstractFileValue
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import FileValueMetadata
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import PermissionNotExistsError

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


def make_iiif_uri_value_graph(
    iiif_uri: IIIFUriInfo, res_bn: BNode, permissions_lookup: dict[str, Permissions]
) -> tuple[Graph, URIRef]:
    """
    Creates a graph with the IIIF-URI Link

    Args:
        iiif_uri: Information about the IIIF URI
        res_bn: Blank-node of the resource
        permissions_lookup: to resolve the permissions

    Returns:
        Graph with the IIIF-URI Value
    """
    iiif_bn = BNode()
    permissions = _get_permission_str(iiif_uri.permissions, permissions_lookup)
    metadata = FileValueMetadata(permissions)
    g = _add_metadata(iiif_bn, metadata)
    knora_prop = KNORA_API.hasStillImageFileValue
    g.add((res_bn, knora_prop, iiif_bn))
    g.add((iiif_bn, RDF.type, KNORA_API.StillImageExternalFileValue))
    g.add((iiif_bn, KNORA_API.fileValueHasExternalUrl, Literal(iiif_uri.value)))
    return g, knora_prop


def make_file_value_graph(
    bitstream_info: BitstreamInfo, res_bn: BNode, permission_lookup: dict[str, Permissions]
) -> tuple[Graph, URIRef]:
    """
    Creates a graph with the File Value information.

    Args:
        bitstream_info: Information about the previously uploaded file
        res_bn: Blank-node of the resource
        permission_lookup: to resolve the permissions

    Returns:
        Graph with the File Value
    """
    local_file = Path(bitstream_info.local_file)
    file_ending = local_file.suffix[1:].lower()
    file_type = _get_file_type_info(file_ending, bitstream_info.local_file)
    internal_filename = bitstream_info.internal_file_name
    permissions = _get_permission_str(bitstream_info.permissions, permission_lookup)
    metadata = FileValueMetadata(permissions)
    file_value = AbstractFileValue(internal_filename, metadata)
    return _make_file_value_graph(file_value, file_type, res_bn), file_type.knora_prop


def _get_file_type_info(file_ending: str, local_file: str) -> RDFPropTypeInfo:
    match file_ending:
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            return ARCHIVE_FILE_VALUE
        case "mp3" | "wav":
            return AUDIO_FILE_VALUE
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            return DOCUMENT_FILE_VALUE
        case "mp4":
            return MOVING_IMAGE_FILE_VALUE
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            return STILL_IMAGE
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv":
            return TEXT_FILE_VALUE
        case _:
            raise BaseError(f"Unknown file ending '{file_ending}' for file '{local_file}'")


def _make_file_value_graph(file_value: AbstractFileValue, type_info: RDFPropTypeInfo, res_bn: BNode) -> Graph:
    file_bn = BNode()
    g = _add_metadata(file_bn, file_value.metadata)
    g.add((res_bn, type_info.knora_prop, file_bn))
    g.add((file_bn, RDF.type, type_info.knora_type))
    g.add((file_bn, KNORA_API.fileValueHasFilename, Literal(file_value.internal_filename, datatype=XSD.string)))
    return g


def _add_metadata(file_bn: BNode, metadata: FileValueMetadata) -> Graph:
    g = Graph()
    if metadata.permissions:
        g.add((file_bn, KNORA_API.hasPermissions, Literal(metadata.permissions, datatype=XSD.string)))
    return g


def _get_permission_str(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> str | None:
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return str(per)
    return None
