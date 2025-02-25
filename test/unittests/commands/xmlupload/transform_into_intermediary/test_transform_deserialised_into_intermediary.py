# mypy: disable-error-code="no-untyped-def"

import pytest
import regex

from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.res import MigrationMetadata
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
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import _resolve_permission
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    _resolve_value_metadata,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    _transform_file_value,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    _transform_one_resource,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import _transform_one_value
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.models.datetimestamp import DateTimeStamp
from dsp_tools.models.exceptions import InvalidInputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.utils.date_util import Era
from dsp_tools.utils.date_util import SingleDate
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

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"

# this enables the usage of the fixtures defined in that file
pytest_plugins = "test.unittests.commands.validate_data.fixtures.data_deserialised"


@pytest.fixture
def permission_good() -> PropertyObject:
    return PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "open", TripleObjectType.STRING)


@pytest.fixture
def permission_inexistent() -> PropertyObject:
    return PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "does-not-exist", TripleObjectType.STRING)


@pytest.fixture
def comment_prop_obj() -> PropertyObject:
    return PropertyObject(TriplePropertyType.KNORA_COMMENT_ON_VALUE, "Comment", TripleObjectType.STRING)


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
    assert failure.resource_id == "resource_inexistent_permissions"
    assert failure.failure_msg == "Could not find permissions for value: does-not-exist"


class TestTransformOneResource:
    def test_no_values(self, resource_deserialised_no_values):
        result = _transform_one_resource(resource_deserialised_no_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == "resource_deserialised_no_values"
        assert result.type_iri == f"{ONTO_STR}ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_values(self, resource_deserialised_with_values):
        result = _transform_one_resource(resource_deserialised_with_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == "resource_deserialised_with_values"
        assert result.type_iri == f"{ONTO_STR}ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_asset(self, resource_deserialised_with_asset):
        result = _transform_one_resource(resource_deserialised_with_asset, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == "resource_deserialised_with_asset"
        assert result.type_iri == f"{ONTO_STR}ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_migration_metadata(self, resource_with_migration_metadata):
        result = _transform_one_resource(resource_with_migration_metadata, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryResource)
        assert result.res_id == "resource_with_migration_metadata"
        assert result.type_iri == f"{ONTO_STR}ClassWithEverything"
        assert result.label == "lbl"
        assert not result.permissions
        assert not result.values
        assert not result.file_value
        assert not result.iiif_uri
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "bla"
        assert str(metadata.creation_date) == "1999-12-31T23:59:59.9999999+01:00"

    def test_inexistent_permission(self, resource_inexistent_permissions):
        result = _transform_one_resource(resource_inexistent_permissions, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == "resource_inexistent_permissions"
        assert result.failure_msg == "Could not find permissions for value: does-not-exist"

    def test_with_failing_value(self, resource_with_failing_value):
        result = _transform_one_resource(resource_with_failing_value, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == "resource_with_failing_value"
        assert result.failure_msg == "Could not find permissions for value: does-not-exist"


class TestTransformValues:
    def test_boolean_with_comment(self, comment_prop_obj):
        val = ValueInformation(
            "propIRI",
            "1",
            KnoraValueType.BOOLEAN_VALUE,
            [comment_prop_obj],
        )
        result = _transform_one_value(val, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == "propIRI"
        assert result.value is True
        assert not result.comment
        assert not result.permissions

    def test_boolean_with_comment_and_permissions(self, permission_good):
        val = ValueInformation(
            "propIRI",
            "false",
            KnoraValueType.BOOLEAN_VALUE,
            [
                PropertyObject(TriplePropertyType.KNORA_COMMENT_ON_VALUE, "Comment", TripleObjectType.STRING),
                permission_good,
            ],
        )
        result = _transform_one_value(val, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == "propIRI"
        assert result.value is False
        assert not result.comment
        assert not result.permissions

    def test_val_bool_permissions_good(self, val_bool_permissions_good):
        result = _transform_one_value(val_bool_permissions_good, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryBoolean)
        assert result.prop_iri == "propIRI"
        assert result.value is True
        assert not result.comment
        assert not result.permissions

    def test_val_bool_inexistent_permissions(self, val_bool_inexistent_permissions):
        message = regex.escape("Could not find permissions for value: does-not-exist")
        with pytest.raises(PermissionNotExistsError, match=message):
            _transform_one_value(val_bool_inexistent_permissions, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_color_value_deserialised_corr(self, color_value_deserialised_corr):
        result = _transform_one_value(color_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryColor)
        assert result.prop_iri == f"{ONTO_STR}testColor"
        assert result.value == "#00ff00"
        assert not result.comment
        assert not result.permissions

    def test_date_value_deserialised_corr(self, date_value_deserialised_corr):
        result = _transform_one_value(date_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryDate)
        assert result.prop_iri == f"{ONTO_STR}testSubDate1"
        assert result.value.start.year == 700
        assert result.value.start.era == Era.BCE
        assert isinstance(result.value.end, SingleDate)
        assert result.value.end.year == 600
        assert result.value.end.era == Era.BCE
        assert not result.comment
        assert not result.permissions

    def test_decimal_value_deserialised_corr(self, decimal_value_deserialised_corr):
        result = _transform_one_value(decimal_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryDecimal)
        assert result.prop_iri == f"{ONTO_STR}testDecimalSimpleText"
        assert result.value == 1.2
        assert not result.comment
        assert not result.permissions

    def test_geoname_value_deserialised_corr(self, geoname_value_deserialised_corr):
        result = _transform_one_value(geoname_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryGeoname)
        assert result.prop_iri == f"{ONTO_STR}testGeoname"
        assert result.value == "1241345"
        assert not result.comment
        assert not result.permissions

    def test_int_value_deserialised_corr(self, int_value_deserialised_corr):
        result = _transform_one_value(int_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryInt)
        assert result.prop_iri == f"{ONTO_STR}testIntegerSimpleText"
        assert result.value == 1
        assert not result.comment
        assert not result.permissions

    def test_interval_value_deserialised_corr(self, interval_value_deserialised_corr):
        result = _transform_one_value(interval_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryInterval)
        assert result.prop_iri == f"{ONTO_STR}hasSegmentBounds"
        assert result.value.start == 1
        assert result.value.end == 2
        assert not result.comment
        assert not result.permissions

    def test_link_value_deserialised_corr(self, link_value_deserialised_corr):
        result = _transform_one_value(link_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryLink)
        assert result.prop_iri == f"{ONTO_STR}testHasLinkTo"
        assert result.value == "link-id"
        assert not result.comment
        assert not result.permissions

    def test_link_value_deserialised_none(self, link_value_deserialised_none):
        message = regex.escape(
            "A value of the property http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo is empty."
        )
        with pytest.raises(InvalidInputError, match=message):
            _transform_one_value(link_value_deserialised_none, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_list_value_deserialised_corr(self, list_value_deserialised_corr):
        result = _transform_one_value(list_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryList)
        assert result.prop_iri == f"{ONTO_STR}testListProp"
        assert result.value == "http://rdfh.ch/9999/node"
        assert not result.comment
        assert not result.permissions

    def test_simple_text_deserialised_corr(self, simple_text_deserialised_corr):
        result = _transform_one_value(simple_text_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediarySimpleText)
        assert result.prop_iri == f"{ONTO_STR}testTextarea"
        assert result.value == "simple text"
        assert not result.comment
        assert not result.permissions

    def test_richtext_deserialised_corr(self, richtext_deserialised_corr):
        result = _transform_one_value(richtext_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryRichtext)
        assert result.prop_iri == f"{ONTO_STR}testRichtext"
        assert result.value.xmlstr == "rich text"
        assert not result.comment
        assert not result.permissions

    def test_time_value_deserialised_corr(self, time_value_deserialised_corr):
        result = _transform_one_value(time_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryTime)
        assert result.prop_iri == f"{ONTO_STR}testTimeValue"
        assert result.value == "2019-10-23T13:45:12.01-14:00"
        assert not result.comment
        assert not result.permissions

    def test_uri_value_deserialised_corr(self, uri_value_deserialised_corr):
        result = _transform_one_value(uri_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)
        assert isinstance(result, IntermediaryUri)
        assert result.prop_iri == f"{ONTO_STR}testUriValue"
        assert result.value == "https://dasch.swiss"
        assert not result.comment
        assert not result.permissions

    def test_transform_file_value(self):
        val = ValueInformation("knora-prop", "image.jpg", KnoraValueType.STILL_IMAGE_FILE, [])
        result = _transform_file_value(val, PERMISSION_LOOKUP, "id", "lbl")
        assert result.value == "image.jpg"
        assert not result.metadata.permissions
        assert result.res_id == "id"
        assert result.res_label == "lbl"

    def test_transform_file_value_with_permissions(self, permission_good):
        val = ValueInformation("knora-prop", "image.jpg", KnoraValueType.STILL_IMAGE_FILE, [permission_good])
        result = _transform_file_value(val, PERMISSION_LOOKUP, "id", "lbl")
        assert result.value == "image.jpg"
        isinstance(result.metadata.permissions, Permissions)
        assert result.res_id == "id"
        assert result.res_label == "lbl"


class TestTransformMetadata:
    def test_separate_comment_and_permissions(self, permission_good, comment_prop_obj):
        perm, cmt = _resolve_value_metadata([permission_good, comment_prop_obj], PERMISSION_LOOKUP)
        assert isinstance(perm, Permissions)
        assert cmt == "Comment"

    def test_resolve_permission_good(self):
        result = _resolve_permission("good", PERMISSION_LOOKUP)
        assert result == PERMISSION_LOOKUP["good"]

    def test_resolve_permission_raises(self):
        with pytest.raises(PermissionNotExistsError):
            _resolve_permission("does-not-exist", PERMISSION_LOOKUP)


if __name__ == "__main__":
    pytest.main([__file__])
