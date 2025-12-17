# mypy: disable-error-code="no-untyped-def"
from typing import Any

import pytest

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.project_validate import _check_for_invalid_default_permissions_overrule


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


def test_check_overrule_no_overrule(project_no_overrule: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_no_overrule) is None


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


def test_check_overrule_valid_multiple_inheritance(project_valid_multiple_inheritance: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_valid_multiple_inheritance) is None


@pytest.fixture
def project_cross_ontology_inheritance() -> dict[str, Any]:
    """Project with cross-ontology inheritance"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["onto2:SubImageResource"]},
            "ontologies": [
                {"name": "onto1", "resources": [{"name": "ImageResource", "super": "StillImageRepresentation"}]},
                {"name": "onto2", "resources": [{"name": "SubImageResource", "super": "onto1:ImageResource"}]},
            ],
        }
    }


def test_check_overrule_valid_cross_ontology_inheritance(project_cross_ontology_inheritance: dict[str, Any]) -> None:
    assert _check_for_invalid_default_permissions_overrule(project_cross_ontology_inheritance) is None


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


def test_check_overrule_invalid_wrong_superclass(project_invalid_wrong_superclass: dict[str, Any]) -> None:
    problems = _check_for_invalid_default_permissions_overrule(project_invalid_wrong_superclass)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.INVALID_PERMISSIONS_OVERRULE
    assert "test-onto:PDFResource" in problems.problems[0].problematic_object
    assert "StillImageRepresentation" in problems.problems[0].problematic_object


@pytest.fixture
def project_invalid_missing_resource() -> dict[str, Any]:
    """Project with reference to non-existent resource"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["test-onto:NonExistentResource"]},
            "ontologies": [
                {"name": "test-onto", "resources": [{"name": "ImageResource", "super": "StillImageRepresentation"}]}
            ],
        }
    }


def test_check_overrule_invalid_missing_resource(project_invalid_missing_resource: dict[str, Any]) -> None:
    problems = _check_for_invalid_default_permissions_overrule(project_invalid_missing_resource)
    assert isinstance(problems, CollectedProblems)
    assert len(problems.problems) == 1
    assert problems.problems[0].problem == InputProblemType.UNDEFINED_REFERENCE
    assert "test-onto:NonExistentResource" in problems.problems[0].problematic_object
    assert "not found in ontology" in problems.problems[0].problematic_object


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
