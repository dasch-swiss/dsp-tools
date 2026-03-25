from typing import Any

import pytest
import regex

from dsp_tools.commands.get.get_permissions import _categorize_doaps
from dsp_tools.commands.get.get_permissions import _construct_overrule_object
from dsp_tools.commands.get.get_permissions import _convert_prefixes
from dsp_tools.commands.get.get_permissions import _get_prefixed_iri
from dsp_tools.commands.get.get_permissions import _parse_default_permissions
from dsp_tools.commands.get.get_permissions import _validate_doap_categories
from dsp_tools.commands.get.models.permissions_models import DoapCategories

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
    result = _parse_default_permissions([private_perms])
    assert result.value == "private"
    assert result.error is None


def test_parse_default_permissions_public(public_perms: dict[str, Any]) -> None:
    result = _parse_default_permissions([public_perms])
    assert result.value == "public"
    assert result.error is None


def test_parse_default_permissions_wrong_target(public_perms: dict[str, Any]) -> None:
    public_perms["forGroup"] = f"{USER_IRI_PREFIX}SystemAdmin"
    result = _parse_default_permissions([public_perms])
    assert result.error is not None
    assert regex.search("supported target group for DOAPs is ProjectMember", result.error)


def test_parse_default_permissions_with_creator(public_perms: dict[str, Any]) -> None:
    public_perms["hasPermissions"].append(
        {"additionalInformation": f"{USER_IRI_PREFIX}Creator", "name": "CR", "permissionCode": 16}
    )
    result = _parse_default_permissions([public_perms])
    assert result.error is not None
    assert regex.search(r"'private' \(with 2 elements\), and 'limited_view' \(with 4 elements\)", result.error)


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
    assert result is not None
    assert result.class_doaps == [class_doap_private]
    assert result.prop_doaps == [prop_doap_private]
    assert result.has_img_all_classes_doaps == [img_all_doap]
    assert result.has_img_specific_class_doaps == []

    result2 = _categorize_doaps([class_doap_private, img_specific_doap])
    assert result2 is not None
    assert result2.class_doaps == [class_doap_private]
    assert result2.prop_doaps == []
    assert result2.has_img_all_classes_doaps == []
    assert result2.has_img_specific_class_doaps == [img_specific_doap]


def test_categorize_doaps_empty() -> None:
    result = _categorize_doaps([])
    assert result is not None
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
    assert _categorize_doaps([invalid_doap]) is None


def test_categorize_doaps_mixed_valid_and_invalid(class_doap_private: dict[str, Any]) -> None:
    """Test that the function fails if any DOAP is invalid, even if others are valid."""
    invalid_doap = {
        "forResourceClass": "",
        "forProject": PROJ_IRI,
        "hasPermissions": [],
    }
    assert _categorize_doaps([class_doap_private, invalid_doap]) is None


def test_validate_doap_categories_valid_all_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_all_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        has_img_all_classes_doaps=[img_all_doap],
        has_img_specific_class_doaps=[],
    )
    assert _validate_doap_categories(categories)


def test_validate_doap_categories_valid_specific_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_specific_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        has_img_all_classes_doaps=[],
        has_img_specific_class_doaps=[img_specific_doap],
    )
    assert _validate_doap_categories(categories)


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
    assert not _validate_doap_categories(categories)


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
    assert not _validate_doap_categories(categories)


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
    assert not _validate_doap_categories(categories)


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
    assert result == {"limited_view": "all"}


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
    assert _construct_overrule_object(categories, {}) is None


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
    assert _construct_overrule_object(categories, {}) is None


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
