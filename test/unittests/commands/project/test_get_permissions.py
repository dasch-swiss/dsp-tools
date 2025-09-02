from typing import Any

import pytest
import regex

from dsp_tools.commands.project.get.get_permissions import _categorize_doaps
from dsp_tools.commands.project.get.get_permissions import _construct_overrule_object
from dsp_tools.commands.project.get.get_permissions import _convert_prefixes
from dsp_tools.commands.project.get.get_permissions import _get_prefixed_iri
from dsp_tools.commands.project.get.get_permissions import _is_legacy_private_pattern
from dsp_tools.commands.project.get.get_permissions import _is_legacy_public_pattern
from dsp_tools.commands.project.get.get_permissions import _parse_default_permissions
from dsp_tools.commands.project.get.get_permissions import _parse_legacy_doaps
from dsp_tools.commands.project.get.get_permissions import _validate_doap_categories
from dsp_tools.commands.project.models.permissions_models import DoapCategories
from dsp_tools.error.exceptions import UnknownDOAPException

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"
PROJ_IRI = "https://api.dev.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"


@pytest.fixture
def class_doap_private() -> dict[str, Any]:
    return {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }


@pytest.fixture
def prop_doap_private() -> dict[str, Any]:
    return {
        "forProperty": "http://www.knora.org/ontology/1234/my-onto#myProperty",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }


@pytest.fixture
def img_all_doap() -> dict[str, Any]:
    return {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ],
    }


@pytest.fixture
def img_specific_doap() -> dict[str, Any]:
    return {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#ImageClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ],
    }


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
    with pytest.raises(UnknownDOAPException, match=regex.escape("supported target group for DOAPs is ProjectMember")):
        _parse_default_permissions([public_perms])


def test_parse_default_permissions_previous_standard(public_perms: dict[str, Any]) -> None:
    public_perms_admin = public_perms.copy()
    public_perms_admin["forGroup"] = f"{USER_IRI_PREFIX}ProjectAdmin"
    assert _parse_default_permissions([public_perms_admin, public_perms]) == "public"


def test_parse_default_permissions_with_creator(public_perms: dict[str, Any]) -> None:
    public_perms["hasPermissions"].append(
        {"additionalInformation": f"{USER_IRI_PREFIX}Creator", "name": "CR", "permissionCode": 16}
    )
    with pytest.raises(
        UnknownDOAPException, match=regex.escape("'private' (with 2 elements), and 'limited_view' (with 4 elements)")
    ):
        _parse_default_permissions([public_perms])


@pytest.mark.parametrize(
    ("input_prefixes", "expected"),
    [
        (
            {"my-onto": "http://0.0.0.0:3333/ontology/1234/my-onto/v2"},
            {"http://www.knora.org/ontology/1234/my-onto": "my-onto"},
        ),
        (
            {
                "my-onto": "http://0.0.0.0:3333/ontology/1234/my-onto/v2",
                "beol": "http://api.dev.dasch.swiss/ontology/0801/beol/v2",
            },
            {
                "http://www.knora.org/ontology/1234/my-onto": "my-onto",
                "http://www.knora.org/ontology/0801/beol": "beol",
            },
        ),
        ({}, {}),
        (
            {"unknown-external-onto": "http://external.com/not-matching-pattern"},
            {},
        ),
    ],
)
def test_convert_prefixes(input_prefixes: dict[str, str], expected: dict[str, str]) -> None:
    result = _convert_prefixes(input_prefixes)
    assert result == expected


def test_categorize_doaps_valid_cases(
    class_doap_private: dict[str, Any],
    prop_doap_private: dict[str, Any],
    img_all_doap: dict[str, Any],
    img_specific_doap: dict[str, Any],
) -> None:
    result = _categorize_doaps([class_doap_private, prop_doap_private, img_all_doap])
    assert result.class_doaps == [class_doap_private]
    assert result.prop_doaps == [prop_doap_private]
    assert result.has_img_all_classes_doaps == [img_all_doap]
    assert result.has_img_specific_class_doaps == []

    result2 = _categorize_doaps([class_doap_private, img_specific_doap])
    assert result2.class_doaps == [class_doap_private]
    assert result2.prop_doaps == []
    assert result2.has_img_all_classes_doaps == []
    assert result2.has_img_specific_class_doaps == [img_specific_doap]


def test_categorize_doaps_empty() -> None:
    result = _categorize_doaps([])
    assert len(result.class_doaps) == 0
    assert len(result.prop_doaps) == 0
    assert len(result.has_img_all_classes_doaps) == 0
    assert len(result.has_img_specific_class_doaps) == 0


@pytest.mark.parametrize(
    "invalid_doap",
    [
        {
            "forProject": PROJ_IRI,
            "hasPermissions": [],
        },
        {
            "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
            "forProperty": "http://www.knora.org/ontology/1234/my-onto#regularProperty",
            "forProject": PROJ_IRI,
            "hasPermissions": [],
        },
        {
            "forResourceClass": None,
            "forProperty": None,
            "forProject": PROJ_IRI,
            "hasPermissions": [],
        },
        {
            "forResourceClass": "",
            "forProject": PROJ_IRI,
            "hasPermissions": [],
        },
        {
            "forProperty": "",
            "forProject": PROJ_IRI,
            "hasPermissions": [],
        },
    ],
)
def test_categorize_doaps_invalid_doap(invalid_doap: dict[str, Any]) -> None:
    with pytest.raises(UnknownDOAPException):
        _categorize_doaps([invalid_doap])


def test_categorize_doaps_mixed_valid_and_invalid(class_doap_private: dict[str, Any]) -> None:
    """Test that the function fails if any DOAP is invalid, even if others are valid."""
    invalid_doap = {
        "forResourceClass": "",
        "forProject": PROJ_IRI,
        "hasPermissions": [],
    }
    with pytest.raises(UnknownDOAPException):
        _categorize_doaps([class_doap_private, invalid_doap])


def test_validate_doap_categories_valid_all_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_all_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        has_img_all_classes_doaps=[img_all_doap],
        has_img_specific_class_doaps=[],
    )
    _validate_doap_categories(categories)


def test_validate_doap_categories_valid_specific_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_specific_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[img_specific_doap],
    )
    _validate_doap_categories(categories)


def test_validate_doap_categories_invalid_private_wrong_count() -> None:
    class_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16}
        ],
    }
    categories = DoapCategories(
        class_doaps=[class_doap],
        prop_doaps=[],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[],
    )
    with pytest.raises(UnknownDOAPException, match=r"'private' is defined as CR ProjectAdmin\|D ProjectMember"):
        _validate_doap_categories(categories)


def test_validate_doap_categories_invalid_private_wrong_names() -> None:
    prop_doap = {
        "forProperty": "http://www.knora.org/ontology/1234/my-onto#myProp",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "WRONG", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[prop_doap],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[],
    )
    with pytest.raises(UnknownDOAPException, match=r"'private' is defined as CR ProjectAdmin\|D ProjectMember"):
        _validate_doap_categories(categories)


def test_validate_doap_categories_invalid_limited_view_wrong_count() -> None:
    img_doap = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[img_doap],
        has_img_specific_class_doaps=[],
    )
    with pytest.raises(
        UnknownDOAPException,
        match=r"'limited_view' is defined as CR ProjectAdmin\|D ProjectMember\|RV KnownUser\|RV UnknownUser",
    ):
        _validate_doap_categories(categories)


def test_construct_overrule_object_private_only() -> None:
    class_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
        "hasPermissions": [],
    }
    prop_doap = {
        "forProperty": "http://www.knora.org/ontology/1234/my-onto#myProperty",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[class_doap],
        prop_doaps=[prop_doap],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[],
    )
    prefixes_inverted = {
        "http://www.knora.org/ontology/1234/my-onto": "my-onto",
    }
    result = _construct_overrule_object(categories, prefixes_inverted)
    assert result == {"private": ["my-onto:MyClass", "my-onto:myProperty"]}


def test_construct_overrule_object_limited_view_all() -> None:
    img_doap = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[img_doap],
        has_img_specific_class_doaps=[],
    )
    result = _construct_overrule_object(categories, {})
    assert result == {"limited_view": "all"}  # TODO: This change is fishy


def test_construct_overrule_object_limited_view_specific() -> None:
    img_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#ImageClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[img_doap],
    )
    prefixes_inverted = {
        "http://www.knora.org/ontology/1234/my-onto": "my-onto",
    }
    result = _construct_overrule_object(categories, prefixes_inverted)
    assert result == {"limited_view": ["my-onto:ImageClass"]}


def test_construct_overrule_object_mixed() -> None:
    class_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
        "hasPermissions": [],
    }
    img_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#ImageClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[class_doap],
        prop_doaps=[],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[img_doap],
    )
    prefixes_inverted = {
        "http://www.knora.org/ontology/1234/my-onto": "my-onto",
    }
    result = _construct_overrule_object(categories, prefixes_inverted)
    assert result == {
        "private": ["my-onto:MyClass"],
        "limited_view": ["my-onto:ImageClass"],
    }


def test_construct_overrule_object_empty() -> None:
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[],
    )
    result = _construct_overrule_object(categories, {})
    assert result == {}


def test_construct_overrule_object_invalid_multiple_all_images() -> None:
    img_doap1 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    img_doap2 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[img_doap1, img_doap2],
        has_img_specific_class_doaps=[],
    )
    with pytest.raises(UnknownDOAPException, match="There can only be 1 all-images DOAP"):
        _construct_overrule_object(categories, {})


def test_construct_overrule_object_invalid_mixed_image_types() -> None:
    all_img_doap = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    specific_img_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#ImageClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        has_img_all_classes_doaps=[all_img_doap],
        has_img_specific_class_doaps=[specific_img_doap],
    )
    with pytest.raises(UnknownDOAPException, match="If there is a DOAP for all images, there cannot be DOAPs"):
        _construct_overrule_object(categories, {})


@pytest.mark.parametrize(
    ("full_iri", "prefixes_inverted", "expected"),
    [
        (
            "http://www.knora.org/ontology/1234/my-onto#MyClass",
            {"http://www.knora.org/ontology/1234/my-onto": "my-onto"},
            "my-onto:MyClass",
        ),
        (
            "http://www.knora.org/ontology/ABCD/other-onto#SomeProperty",
            {"http://www.knora.org/ontology/ABCD/other-onto": "other-onto"},
            "other-onto:SomeProperty",
        ),
        (
            "http://www.knora.org/ontology/1234/my-onto#ComplexName",
            {
                "http://www.knora.org/ontology/1234/my-onto": "my-onto",
                "http://www.knora.org/ontology/ABCD/other-onto": "other-onto",
            },
            "my-onto:ComplexName",
        ),
    ],
)
def test_get_prefixed_iri_valid_cases(full_iri: str, prefixes_inverted: dict[str, str], expected: str) -> None:
    result = _get_prefixed_iri(full_iri, prefixes_inverted)
    assert result == expected


def test_get_prefixed_iri_missing_prefix() -> None:
    full_iri = "http://www.knora.org/ontology/1234/my-onto#MyClass"
    prefixes_inverted = {"http://www.knora.org/ontology/ABCD/other-onto": "other-onto"}
    with pytest.raises(ValueError, match="belongs to an unknown ontology"):
        _get_prefixed_iri(full_iri, prefixes_inverted)


def test_get_prefixed_iri_no_hash_separator() -> None:
    full_iri = "http://www.knora.org/ontology/1234/my-onto/MyClass"
    prefixes_inverted = {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
    with pytest.raises(ValueError, match="is not a valid full IRI"):
        _get_prefixed_iri(full_iri, prefixes_inverted)


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
    assert _parse_legacy_doaps(legacy_private_doap_D) == "private"
    assert _parse_legacy_doaps(legacy_private_doap_M) == "private"


def test_parse_legacy_doaps_public(
    legacy_public_doap_with_creator: list[dict[str, Any]], legacy_public_doap_without_creator: list[dict[str, Any]]
) -> None:
    assert _parse_legacy_doaps(legacy_public_doap_with_creator) == "public"
    assert _parse_legacy_doaps(legacy_public_doap_without_creator) == "public"


def test_parse_legacy_doaps_unknown_pattern() -> None:
    wrong_perms = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "V", "permissionCode": 16},
    ]
    unknown_doap = [
        {"forGroup": f"{USER_IRI_PREFIX}ProjectAdmin", "forProject": PROJ_IRI, "hasPermissions": wrong_perms},
        {"forGroup": f"{USER_IRI_PREFIX}ProjectMember", "forProject": PROJ_IRI, "hasPermissions": wrong_perms},
    ]
    assert _parse_legacy_doaps(unknown_doap) is None


def test_is_legacy_private_pattern_valid(
    legacy_private_doap_D: list[dict[str, Any]], legacy_private_doap_M: list[dict[str, Any]]
) -> None:
    """Test recognition of valid legacy private pattern"""
    assert _is_legacy_private_pattern(legacy_private_doap_D) is True
    assert _is_legacy_private_pattern(legacy_private_doap_M) is True
    assert _is_legacy_public_pattern(legacy_private_doap_D) is False
    assert _is_legacy_public_pattern(legacy_private_doap_M) is False


def test_is_legacy_public_pattern_valid(
    legacy_public_doap_with_creator: list[dict[str, Any]], legacy_public_doap_without_creator: list[dict[str, Any]]
) -> None:
    """Test recognition of valid legacy private pattern"""
    assert _is_legacy_private_pattern(legacy_public_doap_with_creator) is False
    assert _is_legacy_private_pattern(legacy_public_doap_without_creator) is False
    assert _is_legacy_public_pattern(legacy_public_doap_with_creator) is True
    assert _is_legacy_public_pattern(legacy_public_doap_without_creator) is True


def test_is_legacy_pattern_wrong_count() -> None:
    """Test that wrong number of DOAPs is rejected"""
    single_doap = {
        "forGroup": f"{USER_IRI_PREFIX}ProjectAdmin",
        "hasPermissions": [],
    }
    assert _is_legacy_private_pattern([single_doap]) is False
    assert _is_legacy_public_pattern([single_doap]) is False


# def test_is_legacy_pattern_missing_group(legacy_public_admin_doap: dict[str, Any]) -> None:
#     """Test that missing ProjectMember group is rejected"""
#     assert _is_legacy_public_pattern([legacy_public_admin_doap]) is False
#     assert _is_legacy_private_pattern([legacy_private_admin_doap]) is False


# def test_parse_default_permissions_invalid_legacy_falls_back() -> None:
#     """Test that invalid legacy patterns fall back to new-style parsing and fail appropriately"""
#     invalid_legacy = {
#         "forGroup": f"{USER_IRI_PREFIX}ProjectAdmin",
#         "forProject": PROJ_IRI,
#         "hasPermissions": [
#             {"additionalInformation": f"{USER_IRI_PREFIX}WrongGroup", "name": "CR", "permissionCode": 16},
#         ],
#     }
#     # Should fail because it's not valid legacy and also not valid new-style
#     with pytest.raises(UnknownDOAPException):
#         _parse_default_permissions([invalid_legacy])
