import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _get_abstract_file_value
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_migration_metadata
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_resource
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileIIIFUri
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFilePlaceholder
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValueValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.rdf_constants import KNORA_API
from dsp_tools.utils.rdf_constants import URN_DASCH_PLACEHOLDER
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")

FILE_METADATA = ProcessedFileMetadata(license_iri="license", copyright_holder="holder", authorships=["author"])
RESOURCE_TYPE = URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource")
LABEL = Literal("Resource Label", datatype=XSD.string)
PROJECT_IRI = URIRef("http://rdfh.ch/9999/project")


@pytest.fixture
def migration_metadata() -> MigrationMetadata:
    return MigrationMetadata(
        "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA", DateTimeStamp("1999-12-31T23:59:59.9999999+01:00")
    )


def test_make_resource_mandatory_only() -> None:
    res = ProcessedResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        migration_metadata=None,
    )
    res_bn = BNode()
    res_graph = _make_resource(res, res_bn, PROJECT_IRI)
    assert len(res_graph) == 3
    assert next(res_graph.objects(res_bn, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_bn, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_bn, KNORA_API.attachedToProject)) == PROJECT_IRI


def test_make_resource_permissions() -> None:
    res = ProcessedResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]}),
        values=[],
        file_value=None,
        migration_metadata=None,
    )
    res_bn = BNode()
    res_graph = _make_resource(res, res_bn, PROJECT_IRI)
    assert len(res_graph) == 4
    assert next(res_graph.objects(res_bn, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_bn, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_bn, KNORA_API.attachedToProject)) == PROJECT_IRI
    permissions = next(res_graph.objects(res_bn, KNORA_API.hasPermissions))
    assert permissions == Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)


def test_make_resource_migration_metadata() -> None:
    res = ProcessedResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        migration_metadata=None,
    )
    res_iri = URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")
    res_graph = _make_resource(res, res_iri, PROJECT_IRI)
    assert len(res_graph) == 3
    assert next(res_graph.objects(res_iri, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_iri, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_iri, KNORA_API.attachedToProject)) == PROJECT_IRI


def test_make_migration_metadata_with_date(migration_metadata: MigrationMetadata) -> None:
    res_iri = URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")
    graph = _make_migration_metadata(migration_metadata, res_iri)
    assert len(graph) == 1
    creation_date = next(graph.objects(res_iri, KNORA_API.creationDate))
    assert creation_date == Literal("1999-12-31T23:59:59.9999999+01:00", datatype=XSD.dateTimeStamp)


def test_make_migration_metadata_no_date() -> None:
    res_iri = URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")
    migration_data = MigrationMetadata("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA", None)
    graph = _make_migration_metadata(migration_data, res_iri)
    assert len(graph) == 0


def test_get_abstract_file_value_iiif() -> None:
    file_val = ProcessedFileValue(
        value=ProcessedFileIIIFUri(value="https://iiif.example.com/image"),
        value_type=KnoraFileValueType.STILL_IMAGE_IIIF,
        metadata=FILE_METADATA,
    )
    result = _get_abstract_file_value(file_val, None)
    assert result.value == "https://iiif.example.com/image"
    assert result.prop_to_filename == KNORA_API.stillImageFileValueHasExternalUrl


def test_get_abstract_file_value_bitstream() -> None:
    file_val = ProcessedFileValue(
        value=ProcessedFileBitstream(value="original.jpg", res_id="res_1"),
        value_type=KnoraFileValueType.STILL_IMAGE_FILE,
        metadata=FILE_METADATA,
    )
    bitstream = BitstreamInfo(internal_file_name="abcdef.jp2")
    result = _get_abstract_file_value(file_val, bitstream)
    assert result.value == "abcdef.jp2"
    assert result.prop_to_filename == KNORA_API.fileValueHasFilename


def test_get_abstract_file_value_placeholder() -> None:
    file_val = ProcessedFileValue(
        value=ProcessedFilePlaceholder(),
        value_type=KnoraFileValueType.STILL_IMAGE_FILE,
        metadata=FILE_METADATA,
    )
    result = _get_abstract_file_value(file_val, None)
    assert result.value == URN_DASCH_PLACEHOLDER
    assert result.prop_to_filename == KNORA_API.fileValueHasFilename


def test_get_abstract_file_value_unreachable() -> None:
    file_val = ProcessedFileValue(
        value=ProcessedFileValueValue(value="x"),
        value_type=KnoraFileValueType.STILL_IMAGE_FILE,
        metadata=FILE_METADATA,
    )
    with pytest.raises(UnreachableCodeError):
        _get_abstract_file_value(file_val, None)
