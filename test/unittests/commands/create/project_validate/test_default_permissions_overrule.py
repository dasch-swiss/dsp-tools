# mypy: disable-error-code="no-untyped-def"
from typing import Any

import pytest

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.project_validate import _check_for_invalid_default_permissions_overrule
from dsp_tools.commands.create.project_validate import _get_still_image_classes
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from test.unittests.commands.create.constants import ONTO_IRI
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR

KNORA_STILL_IMAGE = f"{KNORA_API_PREFIX}StillImageRepresentation"


@pytest.fixture
def project_no_overrule() -> dict[str, Any]:
    """Project definition without default_permissions_overrule"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "ontologies": [{"name": "test-onto", "resources": [{"name": "TestResource", "super": "Resource"}]}],
        }
    }


# TODO: not possible make "private"
def test_check_overrule_no_overrule(project_no_overrule: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_no_overrule) is None


# TODO: make public no overrule


@pytest.fixture
def project_no_limited_view() -> dict[str, Any]:
    """Project definition with overrule but no limited_view"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"private": ["test-onto:TestResource"]},
            "ontologies": [{"name": "test-onto", "resources": [{"name": "TestResource", "super": "Resource"}]}],
        }
    }


def test_check_overrule_no_limited_view(project_no_limited_view: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_no_limited_view) is None


@pytest.fixture
def project_limited_view_all() -> dict[str, Any]:
    """Project definition with limited_view: 'all'"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions": "public",
            "default_permissions_overrule": {"limited_view": "all"},
            "ontologies": [{"name": "test-onto", "resources": [{"name": "Img", "super": "StillImageRepresentation"}]}],
        }
    }


def test_check_overrule_limited_view_all(project_limited_view_all: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_limited_view_all) is None


@pytest.fixture
def project_valid_direct_inheritance() -> dict[str, Any]:
    """Project with valid direct inheritance from StillImageRepresentation"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:ImageResource"]},
            "ontologies": [
                {"name": "test-onto", "resources": [{"name": "ImageResource", "super": "StillImageRepresentation"}]}
            ],
        }
    }


# TODO: move to get is-stillimage
def test_check_overrule_valid_direct_inheritance(project_valid_direct_inheritance: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_valid_direct_inheritance) is None


@pytest.fixture
def project_valid_indirect_inheritance() -> dict[str, Any]:
    """Project with valid indirect inheritance through another resource"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:SubImageResource"]},
            "ontologies": [
                {
                    "name": "test-onto",
                    "resources": [
                        {"name": "ImageResource", "super": "StillImageRepresentation"},
                        {"name": "SubImageResource", "super": ":ImageResource"},
                    ],
                }
            ],
        }
    }


# TODO: move to get is-stillimage
def test_check_overrule_valid_indirect_inheritance(project_valid_indirect_inheritance: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_valid_indirect_inheritance) is None


@pytest.fixture
def project_valid_multiple_inheritance() -> dict[str, Any]:
    """Project with valid multiple inheritance (list format)"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:ImageResource"]},
            "ontologies": [
                {
                    "name": "test-onto",
                    "resources": [{"name": "ImageResource", "super": ["StillImageRepresentation", "Resource"]}],
                }
            ],
        }
    }


# TODO: move to get is-stillimage
def test_check_overrule_valid_multiple_inheritance(project_valid_multiple_inheritance: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_valid_multiple_inheritance) is None


@pytest.fixture
def project_invalid_wrong_superclass() -> dict[str, Any]:
    """Project with invalid superclass (not StillImageRepresentation)"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:PDFResource"]},
            "ontologies": [
                {"name": "test-onto", "resources": [{"name": "PDFResource", "super": "DocumentRepresentation"}]}
            ],
        }
    }


# TODO: move is-stillimage
def test_check_overrule_invalid_wrong_superclass(project_invalid_wrong_superclass: dict[str, Any]) -> None:
    problems = _check_for_invalid_default_permissions_overrule(project_invalid_wrong_superclass)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.INVALID_PERMISSIONS_OVERRULE
    assert "test-onto:PDFResource" in problems.problems[0].problematic_object
    assert "StillImageRepresentation" in problems.problems[0].problematic_object


@pytest.fixture
def project_circular_reference() -> dict[str, Any]:
    """Project with circular inheritance (should be handled gracefully)"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:Resource1"]},
            "ontologies": [
                {
                    "name": "test-onto",
                    "resources": [
                        {"name": "Resource1", "super": ":Resource2"},
                        {"name": "Resource2", "super": ":Resource1"},
                    ],
                }
            ],
        }
    }


# TODO: check should not be here
def test_check_overrule_circular_reference(project_circular_reference: dict[str, Any]) -> None:
    problems = _check_for_invalid_default_permissions_overrule(project_circular_reference)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.INVALID_PERMISSIONS_OVERRULE
    assert "test-onto:Resource1" in problems.problems[0].problematic_object
    assert "StillImageRepresentation" in problems.problems[0].problematic_object


@pytest.fixture
def project_mixed_valid_invalid() -> dict[str, Any]:
    """Project with mixed valid and invalid classes"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {
                "limited_view": [
                    "test-onto:ImageResource",  # Valid
                    "test-onto:PDFResource",  # Invalid
                    "test-onto:SubImageResource",  # Valid
                ]
            },
            "ontologies": [
                {
                    "name": "test-onto",
                    "resources": [
                        {"name": "ImageResource", "super": "StillImageRepresentation"},
                        {"name": "PDFResource", "super": "DocumentRepresentation"},
                        {"name": "SubImageResource", "super": ":ImageResource"},
                    ],
                }
            ],
        }
    }


def test_check_overrule_mixed_valid_invalid(project_mixed_valid_invalid: dict[str, Any]) -> None:
    problems = _check_for_invalid_default_permissions_overrule(project_mixed_valid_invalid)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.INVALID_PERMISSIONS_OVERRULE
    assert "test-onto:PDFResource" in problems.problems[0].problematic_object
    assert "ImageResource" not in problems.problems[0].problematic_object
    assert "SubImageResource" not in problems.problems[0].problematic_object


class TestGetStillImageClasses:
    def test_no_still_image_classes(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}TextResource",
                labels={"en": "Text"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}PDFResource",
                labels={"en": "PDF"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}DocumentRepresentation"],
                onto_iri=ONTO_IRI,
            ),
        ]
        result = _get_still_image_classes(classes)
        assert result == set()

    def test_direct_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Painting",
                labels={"en": "Painting"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
        ]
        result = _get_still_image_classes(classes)
        assert result == {f"{ONTO_NAMESPACE_STR}Photo", f"{ONTO_NAMESPACE_STR}Painting"}

    def test_deep_inheritance(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level1",
                labels={"en": "L1"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level2",
                labels={"en": "L2"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level1", f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level3",
                labels={"en": "L3"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level2"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level4",
                labels={"en": "L4"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level3"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level5",
                labels={"en": "L5"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level4"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level6",
                labels={"en": "L6"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level5"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Level7",
                labels={"en": "L7"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Level6"],
                onto_iri=ONTO_IRI,
            ),
        ]
        result = _get_still_image_classes(classes)
        assert result == {
            f"{ONTO_NAMESPACE_STR}Level1",
            f"{ONTO_NAMESPACE_STR}Level2",
            f"{ONTO_NAMESPACE_STR}Level3",
            f"{ONTO_NAMESPACE_STR}Level4",
            f"{ONTO_NAMESPACE_STR}Level5",
            f"{ONTO_NAMESPACE_STR}Level6",
            f"{ONTO_NAMESPACE_STR}Level7",
        }

    def test_complex_multi_branch_hierarchy(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Painting",
                labels={"en": "Painting"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}DigitalPhoto",
                labels={"en": "Digital"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}FilmPhoto",
                labels={"en": "Film"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}OilPainting",
                labels={"en": "Oil"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Painting"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Watercolor",
                labels={"en": "Water"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Painting"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}HDRPhoto",
                labels={"en": "HDR"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}DigitalPhoto"],
                onto_iri=ONTO_IRI,
            ),
        ]
        result = _get_still_image_classes(classes)
        assert result == {
            f"{ONTO_NAMESPACE_STR}Photo",
            f"{ONTO_NAMESPACE_STR}Painting",
            f"{ONTO_NAMESPACE_STR}DigitalPhoto",
            f"{ONTO_NAMESPACE_STR}FilmPhoto",
            f"{ONTO_NAMESPACE_STR}OilPainting",
            f"{ONTO_NAMESPACE_STR}Watercolor",
            f"{ONTO_NAMESPACE_STR}HDRPhoto",
        }

    def test_mixed_still_image_and_other_classes(self) -> None:
        classes = [
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Photo",
                labels={"en": "Photo"},
                comments={},
                supers=[KNORA_STILL_IMAGE],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}DigitalPhoto",
                labels={"en": "Digital"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}Photo"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}PDF",
                labels={"en": "PDF"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}DocumentRepresentation"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}ArchivePDF",
                labels={"en": "Archive"},
                comments={},
                supers=[f"{ONTO_NAMESPACE_STR}PDF"],
                onto_iri=ONTO_IRI,
            ),
            ParsedClass(
                name=f"{ONTO_NAMESPACE_STR}Text",
                labels={"en": "Text"},
                comments={},
                supers=[f"{KNORA_API_PREFIX}Resource"],
                onto_iri=ONTO_IRI,
            ),
        ]
        result = _get_still_image_classes(classes)
        assert result == {f"{ONTO_NAMESPACE_STR}Photo", f"{ONTO_NAMESPACE_STR}DigitalPhoto"}
