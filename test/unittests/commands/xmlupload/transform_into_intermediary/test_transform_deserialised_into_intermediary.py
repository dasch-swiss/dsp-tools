# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.res import ResourceInputConversionFailure
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDate
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInterval
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryList
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    _transform_one_property,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    _transform_one_resource,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.models.datetimestamp import DateTimeStamp
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

PERMISSION_LOOKUP = {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}
LISTNODE_LOOKUP = {"list / node": "http://rdfh.ch/9999/node"}


@pytest.fixture
def permission_good() -> PropertyObject:
    return PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "open", TripleObjectType.STRING)


@pytest.fixture
def permission_inexistent() -> PropertyObject:
    return PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "does-not-exist", TripleObjectType.STRING)


@pytest.fixture
def val_bool_inexistent_permissions(permission_inexistent) -> ValueInformation:
    return ValueInformation("propIRI", "true", KnoraValueType.BOOLEAN_VALUE, [permission_inexistent])


@pytest.fixture
def val_bool_permissions_good(permission_good) -> ValueInformation:
    return ValueInformation("propIRI", "true", KnoraValueType.BOOLEAN_VALUE, [permission_good])


@pytest.fixture
def resource_inexistent_permissions(permission_inexistent) -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_inexistent_permissions", [permission_inexistent], [], None, MigrationMetadataDeserialised()
    )


@pytest.fixture
def resource_with_failing_value(val_bool_inexistent_permissions) -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_with_failing_value", [], [val_bool_inexistent_permissions], None, MigrationMetadataDeserialised()
    )


@pytest.fixture
def resource_with_migration_metadata() -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_with_migration_metadata",
        [],
        [],
        None,
        MigrationMetadataDeserialised(
            "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
            "ark:/72163/4123-43xc6ivb931-a.2022829",
            DateTimeStamp("1999-12-31T23:59:59.9999999+01:00"),
        ),
    )


def test_transform_all_resources_into_intermediary_resources_success(
    resource_deserialised_with_values, resource_deserialised_with_asset
):
    result = transform_all_resources_into_intermediary_resources(
        DataDeserialised([resource_deserialised_with_values, resource_deserialised_with_asset]),
        PERMISSION_LOOKUP,
        LISTNODE_LOOKUP,
    )
    assert not result.resource_failures
    transformed = result.transformed_resources
    assert len(transformed) == 2


def test_transform_all_resources_into_intermediary_resources_failure(
    resource_inexistent_permissions, resource_deserialised_no_values
):
    result = transform_all_resources_into_intermediary_resources(
        DataDeserialised([resource_inexistent_permissions, resource_deserialised_no_values]),
        PERMISSION_LOOKUP,
        LISTNODE_LOOKUP,
    )
    assert len(result.resource_failures) == 1
    assert len(result.transformed_resources) == 1
    failure = result.resource_failures.pop(0)
    assert failure.resource_id == ""
    assert failure.failure_msg


class TestTransformOneResource:
    def test_no_values(self, resource_deserialised_no_values):
        result = _transform_one_resource(resource_deserialised_no_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == ""
        assert result.type_iri == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_values(self, resource_deserialised_with_values):
        result = _transform_one_resource(resource_deserialised_with_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == ""
        assert result.type_iri == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_asset(self, resource_deserialised_with_asset):
        result = _transform_one_resource(resource_deserialised_with_asset, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == ""
        assert result.type_iri == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_migration_metadata(self, resource_with_migration_metadata):
        result = _transform_one_resource(resource_with_migration_metadata, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == ""
        assert result.type_iri == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_inexistent_permission(self, resource_inexistent_permissions):
        result = _transform_one_resource(resource_inexistent_permissions, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == ""
        assert result.failure_msg == ""

    def test_with_failing_value(self, resource_with_failing_value):
        result = _transform_one_resource(resource_with_failing_value, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == ""
        assert result.failure_msg == ""


class TestTransformValues:
    def test_(self, boolean_value_deserialised_corr):
        result = _transform_one_property(boolean_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_boolean_value_deserialised_one(self, boolean_value_deserialised_one):
        result = _transform_one_property(boolean_value_deserialised_one, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_boolean_with_comment(self):
        val = ValueInformation(
            "propIRI",
            "true",
            KnoraValueType.BOOLEAN_VALUE,
            [PropertyObject(TriplePropertyType.KNORA_COMMENT_ON_VALUE, "Comment", TripleObjectType.STRING)],
        )
        result = _transform_one_property(val, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_boolean_with_comment_and_permissions(self, permission_good):
        val = ValueInformation(
            "propIRI",
            "true",
            KnoraValueType.BOOLEAN_VALUE,
            [
                PropertyObject(TriplePropertyType.KNORA_COMMENT_ON_VALUE, "Comment", TripleObjectType.STRING),
                permission_good,
            ],
        )
        result = _transform_one_property(val, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_val_bool_permissions_good(self, val_bool_permissions_good):
        result = _transform_one_property(val_bool_permissions_good, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_val_bool_inexistent_permissions(self, val_bool_inexistent_permissions):
        result = _transform_one_property(val_bool_inexistent_permissions, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == ""
        assert result.failure_msg == ""

    def test_color_value_deserialised_corr(self, color_value_deserialised_corr):
        result = _transform_one_property(color_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryColor)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_date_value_deserialised_corr(self, date_value_deserialised_corr):
        result = _transform_one_property(date_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryDate)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_decimal_value_deserialised_corr(self, decimal_value_deserialised_corr):
        result = _transform_one_property(decimal_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryDecimal)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_geoname_value_deserialised_corr(self, geoname_value_deserialised_corr):
        result = _transform_one_property(geoname_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryGeoname)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_int_value_deserialised_corr(self, int_value_deserialised_corr):
        result = _transform_one_property(int_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryInt)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_interval_value_deserialised_corr(self, interval_value_deserialised_corr):
        result = _transform_one_property(interval_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryInterval)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_link_value_deserialised_corr(self, link_value_deserialised_corr):
        result = _transform_one_property(link_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryLink)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_link_value_deserialised_none(self, link_value_deserialised_none):
        result = _transform_one_property(link_value_deserialised_none, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == ""
        assert result.failure_msg == ""

    def test_list_value_deserialised_corr(self, list_value_deserialised_corr):
        result = _transform_one_property(list_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryList)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_simple_text_deserialised_corr(self, simple_text_deserialised_corr):
        result = _transform_one_property(simple_text_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediarySimpleText)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_richtext_deserialised_corr(self, richtext_deserialised_corr):
        result = _transform_one_property(richtext_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryRichtext)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_time_value_deserialised_corr(self, time_value_deserialised_corr):
        result = _transform_one_property(time_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryTime)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions

    def test_uri_value_deserialised_corr(self, uri_value_deserialised_corr):
        result = _transform_one_property(uri_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryUri)
        assert result.prop_iri == ""
        assert result.value == ""
        assert not result.comment
        assert not result.permissions


if __name__ == "__main__":
    pytest.main([__file__])
