import logging
from typing import Any

import pytest
import regex

from dsp_tools.commands.get.get_permissions import _categorize_doaps
from dsp_tools.commands.get.get_permissions import _construct_overrule_object
from dsp_tools.commands.get.get_permissions import _convert_prefixes
from dsp_tools.commands.get.get_permissions import _get_prefixed_iri
from dsp_tools.commands.get.get_permissions import _parse_default_permissions
from dsp_tools.commands.get.get_permissions import _parse_new_style_permissions
from dsp_tools.commands.get.get_permissions import _parse_project_member_perms
from dsp_tools.commands.get.get_permissions import _validate_doap_categories
from dsp_tools.commands.get.get_permissions import _validate_limited_view_doap
from dsp_tools.commands.get.get_permissions import _validate_private_doap
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
def video_all_doap() -> dict[str, Any]:
    return {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasMovingImageFileValue",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ],
    }


@pytest.fixture
def video_specific_doap() -> dict[str, Any]:
    return {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#VideoClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasMovingImageFileValue",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ],
    }


@pytest.fixture
def audio_all_doap() -> dict[str, Any]:
    return {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasAudioFileValue",
        "forProject": PROJ_IRI,
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ],
    }


@pytest.fixture
def audio_specific_doap() -> dict[str, Any]:
    return {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#AudioClass",
        "forProperty": "http://www.knora.org/ontology/knora-base#hasAudioFileValue",
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


def test_parse_default_permissions_wrong_target(public_perms: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    public_perms["forGroup"] = f"{USER_IRI_PREFIX}SystemAdmin"
    with caplog.at_level(logging.WARNING):
        result = _parse_default_permissions([public_perms])
    assert result is None
    assert regex.search(regex.escape("The only supported target group for DOAPs is ProjectMember."), caplog.text)


def test_parse_default_permissions_with_creator(public_perms: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    public_perms["hasPermissions"].append(
        {"additionalInformation": f"{USER_IRI_PREFIX}Creator", "name": "CR", "permissionCode": 16}
    )
    with caplog.at_level(logging.WARNING):
        result = _parse_default_permissions([public_perms])
    assert result is None
    expected_msg = (
        "The only allowed permissions are 'private' (with 2 elements), 'limited_view' or 'public' (with 4 elements)"
    )
    assert regex.search(regex.escape(expected_msg), caplog.text)


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
    assert result.limited_view_all_classes_doaps == [img_all_doap]
    assert result.limited_view_specific_class_doaps == []

    result2 = _categorize_doaps([class_doap_private, img_specific_doap])
    assert result2 is not None
    assert result2.class_doaps == [class_doap_private]
    assert result2.prop_doaps == []
    assert result2.limited_view_all_classes_doaps == []
    assert result2.limited_view_specific_class_doaps == [img_specific_doap]


def test_categorize_doaps_empty() -> None:
    result = _categorize_doaps([])
    assert result is not None
    assert len(result.class_doaps) == 0
    assert len(result.prop_doaps) == 0
    assert len(result.limited_view_all_classes_doaps) == 0
    assert len(result.limited_view_specific_class_doaps) == 0


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
def test_categorize_doaps_invalid_doap(invalid_doap: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        result = _categorize_doaps([invalid_doap])
    assert result is None
    assert "Found DOAPs that do not fit into our system" in caplog.text


def test_categorize_doaps_mixed_valid_and_invalid(
    class_doap_private: dict[str, Any], caplog: pytest.LogCaptureFixture
) -> None:
    """Test that the function fails if any DOAP is invalid, even if others are valid."""
    invalid_doap = {
        "forResourceClass": "",
        "forProject": PROJ_IRI,
        "hasPermissions": [],
    }
    with caplog.at_level(logging.WARNING):
        result = _categorize_doaps([class_doap_private, invalid_doap])
    assert result is None
    assert "Found DOAPs that do not fit into our system" in caplog.text


def test_validate_doap_categories_valid_all_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_all_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        limited_view_all_classes_doaps=[img_all_doap],
        limited_view_specific_class_doaps=[],
    )
    assert _validate_doap_categories(categories)


def test_validate_doap_categories_valid_specific_images(
    class_doap_private: dict[str, Any], prop_doap_private: dict[str, Any], img_specific_doap: dict[str, Any]
) -> None:
    categories = DoapCategories(
        class_doaps=[class_doap_private],
        prop_doaps=[prop_doap_private],
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[img_specific_doap],
    )
    assert _validate_doap_categories(categories)


def test_validate_doap_categories_invalid_private_wrong_count(caplog: pytest.LogCaptureFixture) -> None:
    class_doap = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#MyClass",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16}
        ],
    }
    categories = DoapCategories(
        class_doaps=[class_doap],
        prop_doaps=[],
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[],
    )
    with caplog.at_level(logging.WARNING):
        result = _validate_doap_categories(categories)
    assert result is False
    assert "'private' is defined as CR ProjectAdmin|D ProjectMember" in caplog.text


def test_validate_doap_categories_invalid_private_wrong_names(caplog: pytest.LogCaptureFixture) -> None:
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
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[],
    )
    with caplog.at_level(logging.WARNING):
        result = _validate_doap_categories(categories)
    assert result is False
    assert "'private' is defined as CR ProjectAdmin|D ProjectMember" in caplog.text


def test_validate_doap_categories_invalid_limited_view_wrong_count(caplog: pytest.LogCaptureFixture) -> None:
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
        limited_view_all_classes_doaps=[img_doap],
        limited_view_specific_class_doaps=[],
    )
    with caplog.at_level(logging.WARNING):
        result = _validate_doap_categories(categories)
    assert result is False
    assert "'limited_view' is defined as CR ProjectAdmin|D ProjectMember|RV KnownUser|RV UnknownUser" in caplog.text


def test_validate_doap_categories_logs_all_invalid(caplog: pytest.LogCaptureFixture) -> None:
    """All invalid DOAPs must each log a warning, not just the first one."""
    bad_private = {
        "forResourceClass": "http://www.knora.org/ontology/1234/my-onto#ClassA",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }
    bad_private2 = {
        "forProperty": "http://www.knora.org/ontology/1234/my-onto#propB",
        "hasPermissions": [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ],
    }
    categories = DoapCategories(
        class_doaps=[bad_private],
        prop_doaps=[bad_private2],
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[],
    )
    with caplog.at_level(logging.WARNING):
        result = _validate_doap_categories(categories)
    assert result is False
    assert caplog.text.count("'private' is defined as CR ProjectAdmin|D ProjectMember") == 2


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
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[],
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
        limited_view_all_classes_doaps=[img_doap],
        limited_view_specific_class_doaps=[],
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
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[img_doap],
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
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[img_doap],
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
        limited_view_all_classes_doaps=[],
        limited_view_specific_class_doaps=[],
    )
    result = _construct_overrule_object(categories, {})
    assert result == {}


def test_construct_overrule_object_invalid_multiple_all_images(caplog: pytest.LogCaptureFixture) -> None:
    img_doap1 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    img_doap2 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasMovingImageFileValue",
        "hasPermissions": [],
    }
    img_doap3 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasAudioFileValue",
        "hasPermissions": [],
    }
    img_doap4 = {
        "forProperty": "http://www.knora.org/ontology/knora-base#hasStillImageFileValue",
        "hasPermissions": [],
    }
    categories = DoapCategories(
        class_doaps=[],
        prop_doaps=[],
        limited_view_all_classes_doaps=[img_doap1, img_doap2, img_doap3, img_doap4],
        limited_view_specific_class_doaps=[],
    )
    with caplog.at_level(logging.WARNING):
        result = _construct_overrule_object(categories, {})
    assert result is None
    assert "Found more limited_view DOAPs (no class restriction) than expected file value property types" in caplog.text


def test_construct_overrule_object_invalid_mixed_image_types(caplog: pytest.LogCaptureFixture) -> None:
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
        limited_view_all_classes_doaps=[all_img_doap],
        limited_view_specific_class_doaps=[specific_img_doap],
    )
    with caplog.at_level(logging.WARNING):
        result = _construct_overrule_object(categories, {})
    assert result is None
    assert "Cannot have both all-classes limited_view DOAPs and specific-class limited_view DOAPs" in caplog.text


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


class TestParseProjectMemberPerms:
    def test_private(self) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ]
        assert _parse_project_member_perms(perms) == "private"

    def test_limited_view(self) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
        ]
        assert _parse_project_member_perms(perms) == "limited_view"

    def test_public(self) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
        ]
        assert _parse_project_member_perms(perms) == "public"

    def test_wrong_count(self, caplog: pytest.LogCaptureFixture) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        ]
        with caplog.at_level(logging.WARNING):
            result = _parse_project_member_perms(perms)
        assert result is None
        err_msg = (
            "The only allowed permissions are 'private' (with 2 elements), 'limited_view' or 'public' (with 4 elements)"
        )
        assert regex.search(regex.escape(err_msg), caplog.text)

    def test_wrong_admin_or_member(self, caplog: pytest.LogCaptureFixture) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
        ]
        with caplog.at_level(logging.WARNING):
            result = _parse_project_member_perms(perms)
        assert result is None
        assert regex.search(
            regex.escape("ProjectAdmin must always have CR and ProjectMember must always have D"),
            caplog.text,
        )

    def test_mixed_rv_and_v(self, caplog: pytest.LogCaptureFixture) -> None:
        perms = [
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
        ]
        with caplog.at_level(logging.WARNING):
            result = _parse_project_member_perms(perms)
        assert result is None
        assert regex.search(
            regex.escape("KnownUser and UnknownUser must both have RV (limited_view) or both have V (public)"),
            caplog.text,
        )


class TestValidatePrivateDoap:
    def test_valid(self) -> None:
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            ]
        }
        assert _validate_private_doap(doap) is True

    def test_wrong_count(self, caplog: pytest.LogCaptureFixture) -> None:
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
            ]
        }
        with caplog.at_level(logging.WARNING):
            result = _validate_private_doap(doap)
        assert result is False
        assert regex.search(
            regex.escape("'private' is defined as CR ProjectAdmin|D ProjectMember"),
            caplog.text,
        )

    def test_wrong_names(self, caplog: pytest.LogCaptureFixture) -> None:
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "D", "permissionCode": 8},
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
            ]
        }
        with caplog.at_level(logging.WARNING):
            result = _validate_private_doap(doap)
        assert result is False
        assert regex.search(
            regex.escape("'private' is defined as CR ProjectAdmin|D ProjectMember"),
            caplog.text,
        )


class TestValidateLimitedViewDoap:
    def test_valid(self) -> None:
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
                {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
                {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
            ]
        }
        assert _validate_limited_view_doap(doap) is True

    def test_wrong_count(self, caplog: pytest.LogCaptureFixture) -> None:
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
                {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            ]
        }
        with caplog.at_level(logging.WARNING):
            result = _validate_limited_view_doap(doap)
        assert result is False
        assert regex.search(
            regex.escape("'limited_view' is defined as CR ProjectAdmin|D ProjectMember|RV KnownUser|RV UnknownUser"),
            caplog.text,
        )

    def test_both_rv_same_group(self, caplog: pytest.LogCaptureFixture) -> None:
        """Two KnownUser RV entries (no UnknownUser) must be rejected."""
        doap = {
            "hasPermissions": [
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 16},
                {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 8},
                {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
                {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
            ]
        }
        with caplog.at_level(logging.WARNING):
            result = _validate_limited_view_doap(doap)
        assert result is False
        assert regex.search(
            regex.escape("'limited_view' is defined as CR ProjectAdmin|D ProjectMember|RV KnownUser|RV UnknownUser"),
            caplog.text,
        )


class TestParseNewStylePermissions:
    def test_private(self, private_perms: dict[str, Any]) -> None:
        assert _parse_new_style_permissions([private_perms]) == "private"

    def test_public(self, public_perms: dict[str, Any]) -> None:
        assert _parse_new_style_permissions([public_perms]) == "public"

    def test_unsupported_group(self, public_perms: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
        public_perms["forGroup"] = f"{USER_IRI_PREFIX}SystemAdmin"
        with caplog.at_level(logging.WARNING):
            result = _parse_new_style_permissions([public_perms])
        assert result is None
        assert regex.search(
            regex.escape("The only supported target group for DOAPs is ProjectMember."),
            caplog.text,
        )

    def test_wrong_count(self, private_perms: dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            result = _parse_new_style_permissions([private_perms, private_perms])
        assert result is None
        assert regex.search(
            regex.escape("There must be exactly 1 DOAP for ProjectMember."),
            caplog.text,
        )


class TestMovingImageAndAudioDoapTypes:
    def test_categorize_video_all_doap(self, video_all_doap: dict[str, Any]) -> None:
        result = _categorize_doaps([video_all_doap])
        assert result is not None
        assert result.limited_view_all_classes_doaps == [video_all_doap]
        assert result.limited_view_specific_class_doaps == []

    def test_categorize_audio_all_doap(self, audio_all_doap: dict[str, Any]) -> None:
        result = _categorize_doaps([audio_all_doap])
        assert result is not None
        assert result.limited_view_all_classes_doaps == [audio_all_doap]
        assert result.limited_view_specific_class_doaps == []

    def test_categorize_video_specific_doap(self, video_specific_doap: dict[str, Any]) -> None:
        result = _categorize_doaps([video_specific_doap])
        assert result is not None
        assert result.limited_view_all_classes_doaps == []
        assert result.limited_view_specific_class_doaps == [video_specific_doap]

    def test_categorize_audio_specific_doap(self, audio_specific_doap: dict[str, Any]) -> None:
        result = _categorize_doaps([audio_specific_doap])
        assert result is not None
        assert result.limited_view_all_classes_doaps == []
        assert result.limited_view_specific_class_doaps == [audio_specific_doap]

    def test_categorize_all_three_all_class_doaps(
        self,
        img_all_doap: dict[str, Any],
        video_all_doap: dict[str, Any],
        audio_all_doap: dict[str, Any],
    ) -> None:
        result = _categorize_doaps([img_all_doap, video_all_doap, audio_all_doap])
        assert result is not None
        assert len(result.limited_view_all_classes_doaps) == 3
        assert result.limited_view_specific_class_doaps == []

    def test_validate_video_all_doap(self, video_all_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[video_all_doap],
            limited_view_specific_class_doaps=[],
        )
        assert _validate_doap_categories(categories)

    def test_validate_audio_all_doap(self, audio_all_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[audio_all_doap],
            limited_view_specific_class_doaps=[],
        )
        assert _validate_doap_categories(categories)

    def test_validate_video_specific_doap(self, video_specific_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[],
            limited_view_specific_class_doaps=[video_specific_doap],
        )
        assert _validate_doap_categories(categories)

    def test_validate_audio_specific_doap(self, audio_specific_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[],
            limited_view_specific_class_doaps=[audio_specific_doap],
        )
        assert _validate_doap_categories(categories)

    def test_construct_overrule_video_specific(self, video_specific_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[],
            limited_view_specific_class_doaps=[video_specific_doap],
        )
        prefixes_inverted = {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
        result = _construct_overrule_object(categories, prefixes_inverted)
        assert result == {"limited_view": ["my-onto:VideoClass"]}

    def test_construct_overrule_audio_specific(self, audio_specific_doap: dict[str, Any]) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[],
            limited_view_specific_class_doaps=[audio_specific_doap],
        )
        prefixes_inverted = {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
        result = _construct_overrule_object(categories, prefixes_inverted)
        assert result == {"limited_view": ["my-onto:AudioClass"]}

    def test_construct_overrule_all_three_specific(
        self,
        img_specific_doap: dict[str, Any],
        video_specific_doap: dict[str, Any],
        audio_specific_doap: dict[str, Any],
    ) -> None:
        categories = DoapCategories(
            class_doaps=[],
            prop_doaps=[],
            limited_view_all_classes_doaps=[],
            limited_view_specific_class_doaps=[img_specific_doap, video_specific_doap, audio_specific_doap],
        )
        prefixes_inverted = {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
        result = _construct_overrule_object(categories, prefixes_inverted)
        assert result is not None
        assert set(result["limited_view"]) == {  # type: ignore[arg-type]
            "my-onto:ImageClass",
            "my-onto:VideoClass",
            "my-onto:AudioClass",
        }
