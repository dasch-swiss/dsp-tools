# type: ignore


import pytest

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
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from test.unittests.commands.validate_data.fixtures.data_deserialised import *  # noqa: F403

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
def resource_inexistent_permissions(permission_inexistent) -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_inexistent_permissions", [permission_inexistent], [], None, MigrationMetadata()
    )


@pytest.fixture
def resource_with_failing_value(val_bool_inexistent_permissions) -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_with_failing_value", [], [val_bool_inexistent_permissions], None, MigrationMetadata()
    )


@pytest.fixture
def resource_with_migration_metadata() -> ResourceDeserialised:
    return ResourceDeserialised(
        "resource_with_migration_metadata",
        [],
        [],
        None,
        MigrationMetadata(
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


def test_transform_all_resources_into_intermediary_resources_failure(
    resource_inexistent_permissions, resource_deserialised_no_values
):
    result = transform_all_resources_into_intermediary_resources(
        DataDeserialised([resource_inexistent_permissions, resource_deserialised_no_values]),
        PERMISSION_LOOKUP,
        LISTNODE_LOOKUP,
    )


class TestTransformOneResource:
    def test_no_values(self, resource_deserialised_no_values):
        result = _transform_one_resource(resource_deserialised_no_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_with_values(self, resource_deserialised_with_values):
        result = _transform_one_resource(resource_deserialised_with_values, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_with_asset(self, resource_deserialised_with_asset):
        result = _transform_one_resource(resource_deserialised_with_asset, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_with_migration_metadata(self, resource_with_migration_metadata):
        result = _transform_one_resource(resource_with_migration_metadata, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_inexistent_permission(self, resource_inexistent_permissions):
        result = _transform_one_resource(resource_inexistent_permissions, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_with_failing_value(self, resource_with_failing_value):
        result = _transform_one_resource(resource_with_failing_value, PERMISSION_LOOKUP, LISTNODE_LOOKUP)


class TestTransformValues:
    def test_(self, boolean_value_deserialised_corr):
        result = _transform_one_property(boolean_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_boolean_value_deserialised_one(self, boolean_value_deserialised_one):
        result = _transform_one_property(boolean_value_deserialised_one, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_color_value_deserialised_corr(self, color_value_deserialised_corr):
        result = _transform_one_property(color_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_date_value_deserialised_corr(self, date_value_deserialised_corr):
        result = _transform_one_property(date_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_decimal_value_deserialised_corr(self, decimal_value_deserialised_corr):
        result = _transform_one_property(decimal_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_geoname_value_deserialised_corr(self, geoname_value_deserialised_corr):
        result = _transform_one_property(geoname_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_int_value_deserialised_corr(self, int_value_deserialised_corr):
        result = _transform_one_property(int_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_interval_value_deserialised_corr(self, interval_value_deserialised_corr):
        result = _transform_one_property(interval_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_link_value_deserialised_corr(self, link_value_deserialised_corr):
        result = _transform_one_property(link_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_link_value_deserialised_none(self, link_value_deserialised_none):
        result = _transform_one_property(link_value_deserialised_none, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_list_value_deserialised_corr(self, list_value_deserialised_corr):
        result = _transform_one_property(list_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_simple_text_deserialised_corr(self, simple_text_deserialised_corr):
        result = _transform_one_property(simple_text_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_richtext_deserialised_corr(self, richtext_deserialised_corr):
        result = _transform_one_property(richtext_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_time_value_deserialised_corr(self, time_value_deserialised_corr):
        result = _transform_one_property(time_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)

    def test_uri_value_deserialised_corr(self, uri_value_deserialised_corr):
        result = _transform_one_property(uri_value_deserialised_corr, PERMISSION_LOOKUP, LISTNODE_LOOKUP)


if __name__ == "__main__":
    pytest.main([__file__])
