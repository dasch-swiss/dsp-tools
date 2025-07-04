from typing import Any

import pytest

from dsp_tools.commands.project.get import _parse_default_permissions

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"
PROJ_IRI = "https://api.dev.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"


@pytest.fixture
def private_perms() -> dict[str, Any]:
    perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
    ]
    return {
        "forGroup": f"{USER_IRI_PREFIX}ProjectMember",
        "forProject": PROJ_IRI,
        "hasPermissions": perms,
    }


@pytest.fixture
def public_perms() -> dict[str, Any]:
    perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
    ]
    return {
        "forGroup": f"{USER_IRI_PREFIX}ProjectMember",
        "forProject": PROJ_IRI,
        "hasPermissions": perms,
    }


def test_parse_default_permissions_private(private_perms: dict[str, Any]) -> None:
    assert _parse_default_permissions([private_perms]) == "private"


def test_parse_default_permissions_public(public_perms: dict[str, Any]) -> None:
    assert _parse_default_permissions([public_perms]) == "public"


def test_parse_default_permissions_wrong_target(public_perms: dict[str, Any]) -> None:
    public_perms["forGroup"] = f"{USER_IRI_PREFIX}SystemAdmin"
    assert _parse_default_permissions([public_perms]) == "unknown"


def test_parse_default_permissions_previous_standard(public_perms: dict[str, Any]) -> None:
    public_perms_admin = public_perms.copy()
    public_perms_admin["forGroup"] = f"{USER_IRI_PREFIX}ProjectAdmin"
    assert _parse_default_permissions([public_perms_admin, public_perms]) == "unknown"


def test_parse_default_permissions_with_creator(public_perms: dict[str, Any]) -> None:
    public_perms["hasPermissions"].append(
        {"additionalInformation": f"{USER_IRI_PREFIX}Creator", "name": "CR", "permissionCode": 16}
    )
    assert _parse_default_permissions([public_perms]) == "unknown"
