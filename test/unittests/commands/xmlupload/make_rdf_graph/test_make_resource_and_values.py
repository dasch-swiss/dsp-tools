import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_migration_metadata
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_resource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.rdflib_constants import KNORA_API

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
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
        iiif_uri=None,
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
        iiif_uri=None,
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
        iiif_uri=None,
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
