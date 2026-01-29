from typing import Any

import pytest

from dsp_tools.commands.get.exceptions import UnknownDOAPException
from dsp_tools.commands.get.get_permissions import _parse_default_permissions
from dsp_tools.commands.get.get_permissions_legacy import parse_legacy_doaps

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"
PROJ_IRI = "https://api.dev.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"


@pytest.fixture
def legacy_private_doap_D() -> list[dict[str, Any]]:
    perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
    ]
    return [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": perms},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": perms},
    ]


@pytest.fixture
def legacy_private_doap_M() -> list[dict[str, Any]]:
    perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "M", "permissionCode": 8},
    ]
    return [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": perms},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": perms},
    ]


@pytest.fixture
def legacy_public_doap_with_creator() -> list[dict[str, Any]]:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}Creator", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
    ]
    return [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": perm},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": perm},
    ]


@pytest.fixture
def legacy_public_doap_without_creator() -> list[dict[str, Any]]:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
    ]
    return [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": perm},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": perm},
    ]


def test_parse_legacy_doaps_private(
    legacy_private_doap_D: list[dict[str, Any]], legacy_private_doap_M: list[dict[str, Any]]
) -> None:
    assert parse_legacy_doaps(legacy_private_doap_D) == "private"
    assert parse_legacy_doaps(legacy_private_doap_M) == "private"


def test_parse_legacy_doaps_public(
    legacy_public_doap_with_creator: list[dict[str, Any]], legacy_public_doap_without_creator: list[dict[str, Any]]
) -> None:
    assert parse_legacy_doaps(legacy_public_doap_with_creator) == "public"
    assert parse_legacy_doaps(legacy_public_doap_without_creator) == "public"


def test_parse_legacy_doaps_unknown_pattern() -> None:
    wrong_perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "V", "permissionCode": 16},
    ]
    unknown_doap = [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": wrong_perms},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": wrong_perms},
    ]
    assert parse_legacy_doaps(unknown_doap) is None


def test_is_legacy_pattern_wrong_count() -> None:
    """Test that wrong number of DOAPs and wrong constellation of target groups is rejected"""
    perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
    ]

    single_admin_doap = {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "hasPermissions": perms}
    assert parse_legacy_doaps([single_admin_doap]) is None
    assert parse_legacy_doaps([single_admin_doap, single_admin_doap]) is None
    assert parse_legacy_doaps([single_admin_doap, single_admin_doap, single_admin_doap]) is None

    single_member_doap = {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "hasPermissions": perms}
    assert parse_legacy_doaps([single_member_doap]) is None
    assert parse_legacy_doaps([single_member_doap, single_member_doap]) is None
    assert parse_legacy_doaps([single_member_doap, single_member_doap, single_member_doap]) is None


def test_parse_default_permissions_invalid_legacy_falls_back() -> None:
    """
    Patterns which are neither valid legacy nor valid new-style should first fall back to new-style parsing,
    and then fail during new-style parsing
    """
    invalid_legacy = {
        "forGroup": f"{USER_IRI_PREFIX}ProjectAdmin",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}WrongGroup", "name": "CR", "permissionCode": 16},
        ],
    }
    with pytest.raises(UnknownDOAPException):
        _parse_default_permissions([invalid_legacy])
