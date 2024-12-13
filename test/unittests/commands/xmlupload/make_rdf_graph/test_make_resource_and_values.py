import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import KNORA_API
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_migration_metadata
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import _make_resource
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.datetimestamp import DateTimeStamp

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
RESOURCE_TYPE = URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource")
LABEL = Literal("Resource Label", datatype=XSD.string)
PROJECT_IRI = URIRef("http://rdfh.ch/9999/project")


@pytest.fixture
def lookups() -> IRILookups:
    return IRILookups(
        project_iri="http://rdfh.ch/9999/project",
        id_to_iri=IriResolver({"res_one": "http://rdfh.ch/9999/res_one"}),
        jsonld_context=JSONLDContext({}),
    )


@pytest.fixture
def migration_metadata() -> MigrationMetadata:
    return MigrationMetadata(
        "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA", DateTimeStamp("1999-12-31T23:59:59.9999999+01:00")
    )


def test_make_resource_mandatory_only(lookups: IRILookups) -> None:
    res = IntermediaryResource(
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
    res_graph = _make_resource(res, res_bn, lookups)
    assert len(res_graph) == 0
    assert next(res_graph.objects(res_bn, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_bn, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_bn, KNORA_API.attachedToProject)) == PROJECT_IRI


def test_make_resource_permissions(lookups: IRILookups) -> None:
    res = IntermediaryResource(
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
    res_graph = _make_resource(res, res_bn, lookups)
    assert len(res_graph) == 0
    assert next(res_graph.objects(res_bn, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_bn, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_bn, KNORA_API.attachedToProject)) == PROJECT_IRI
    assert next(res_graph.objects(res_bn, KNORA_API.hasPermissions)) == Literal(
        "CR knora-admin:ProjectAdmin", datatype=XSD.string
    )


def test_make_resource_migration_metadata(lookups: IRILookups, migration_metadata: MigrationMetadata) -> None:
    res = IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        iiif_uri=None,
        migration_metadata=migration_metadata,
    )
    res_iri = URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")
    res_graph = _make_resource(res, res_iri, lookups)
    assert len(res_graph) == 0
    assert next(res_graph.objects(res_iri, RDF.type)) == RESOURCE_TYPE
    assert next(res_graph.objects(res_iri, RDFS.label)) == LABEL
    assert next(res_graph.objects(res_iri, KNORA_API.attachedToProject)) == PROJECT_IRI


def test_make_migration_metadata(migration_metadata: MigrationMetadata) -> None:
    graph = _make_migration_metadata(migration_metadata)
    res_iri = URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")
    assert len(graph) == 0
    creation_date = next(graph.objects(res_iri, KNORA_API.creationDate))
    assert creation_date == Literal("1999-12-31T23:59:59.9999999+01:00", datatype=XSD.dateTimeStamp)
