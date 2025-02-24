from copy import deepcopy

import pytest

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.stash.stash_circular_references_from_intermediary_resource import (
    stash_circular_references,
)
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

PERMISSIONS_LOOKUP = {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}


@pytest.fixture
def link_value_with_permissions_to_res_1() -> ValueInformation:
    return ValueInformation(
        "prop",
        "res_1",
        KnoraValueType.LINK_VALUE,
        [PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "open", TripleObjectType.STRING)],
    )


@pytest.fixture
def link_value_no_permissions_to_res_2() -> ValueInformation:
    return ValueInformation("prop", "res_2", KnoraValueType.LINK_VALUE, [])


@pytest.fixture
def link_value_to_resource_no_links() -> ValueInformation:
    return ValueInformation(
        "prop",
        "res_no_links",
        KnoraValueType.LINK_VALUE,
        [PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, "open", TripleObjectType.STRING)],
    )


@pytest.fixture
def text_value_no_links() -> ValueInformation:
    return ValueInformation("prop", "No links", KnoraValueType.RICHTEXT_VALUE, [])


@pytest.fixture
def text_value_with_link() -> ValueInformation:
    return ValueInformation(
        "prop", 'Link: <a class="salsah-link" href="IRI:res_3:IRI">res_3</a>', KnoraValueType.RICHTEXT_VALUE, []
    )


@pytest.fixture
def resource_1(
    link_value_no_permissions_to_res_2: ValueInformation, link_value_to_resource_no_links: ValueInformation
) -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="res_1",
        property_objects=[],
        values=[link_value_no_permissions_to_res_2, link_value_to_resource_no_links],
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def resource_2(text_value_with_link: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="res_2",
        property_objects=[],
        values=[text_value_with_link],
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def resource_3(link_value_with_permissions_to_res_1: ValueInformation) -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="res_3",
        property_objects=[],
        values=[link_value_with_permissions_to_res_1],
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def resource_no_links() -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="res_no_links", property_objects=[], values=[], asset_value=None, migration_metadata=MigrationMetadata()
    )


def test_stash_circular_references_remove_link_value(
    resource_1: ResourceDeserialised,
    resource_2: ResourceDeserialised,
    resource_3: ResourceDeserialised,
    resource_no_links: ResourceDeserialised,
) -> None:
    resources = [deepcopy(resource_1), deepcopy(resource_2), deepcopy(resource_3), deepcopy(resource_no_links)]
    lookup = {}
    stash = stash_circular_references(resources, lookup, PERMISSIONS_LOOKUP)


def test_stash_circular_references_remove_text_value(
    resource_1: ResourceDeserialised,
    resource_2: ResourceDeserialised,
    resource_3: ResourceDeserialised,
    resource_no_links: ResourceDeserialised,
) -> None:
    resources = [deepcopy(resource_1), deepcopy(resource_2), deepcopy(resource_3), deepcopy(resource_no_links)]
    lookup = {}
    stash = stash_circular_references(resources, lookup, PERMISSIONS_LOOKUP)


if __name__ == "__main__":
    pytest.main([__file__])
