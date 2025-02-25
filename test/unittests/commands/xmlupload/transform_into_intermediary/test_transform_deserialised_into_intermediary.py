# type: ignore


import pytest

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_deserialised_into_intermediary import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

PERMISSION_LOOKUP = {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}
LISTNODE_LOOKUP = {"list / node": "http://rdfh.ch/9999/node"}


@pytest.fixture
def metadata_good() -> list[PropertyObject]:
    return PropertyObject()


@pytest.fixture
def val_bool_failing_permissions() -> ValueInformation:
    return ValueInformation()


@pytest.fixture
def resource_inexistent_permissions() -> ResourceDeserialised:
    return ResourceDeserialised()


@pytest.fixture
def resource_with_failing_value(val_bool_failing_permissions) -> ResourceDeserialised:
    return ResourceDeserialised()


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
    pass


if __name__ == "__main__":
    pytest.main([__file__])
