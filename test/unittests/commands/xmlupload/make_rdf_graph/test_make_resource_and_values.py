import pytest

from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileMetadata
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryIIIFUri
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.models.datetimestamp import DateTimeStamp


@pytest.fixture
def resource_mandatory_only() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        iiif_uri=None,
        migration_metadata=None,
    )


@pytest.fixture
def resource_permissions() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]}),
        values=[],
        file_value=None,
        iiif_uri=None,
        migration_metadata=None,
    )


@pytest.fixture
def resource_value() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[IntermediaryColor("#5d1f1e", "http://0.0.0.0:3333/ontology/9999/onto/v2#hasColor", None, None)],
        file_value=None,
        iiif_uri=None,
        migration_metadata=None,
    )


@pytest.fixture
def resource_file_value() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=IntermediaryFileValue("value", IntermediaryFileMetadata(None)),
        iiif_uri=None,
        migration_metadata=None,
    )


@pytest.fixture
def resource_iiif_uri() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        iiif_uri=IntermediaryIIIFUri("value", IntermediaryFileMetadata(None)),
        migration_metadata=None,
    )


@pytest.fixture
def resource_migration_metadata() -> IntermediaryResource:
    return IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[],
        file_value=None,
        iiif_uri=None,
        migration_metadata=MigrationMetadata(
            "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA", DateTimeStamp("1999-12-31T23:59:59.9999999+01:00")
        ),
    )
