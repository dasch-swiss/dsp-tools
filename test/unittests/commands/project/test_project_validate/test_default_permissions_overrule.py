from typing import Any

import pytest

from dsp_tools.commands.project.create.project_validate import _check_for_invalid_default_permissions_overrule
from dsp_tools.error.exceptions import BaseError


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


@pytest.fixture
def project_invalid_missing_ontology() -> dict[str, Any]:
    """Project with reference to non-existent ontology"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["nonexistent-onto:ImageResource"]},
            "ontologies": [
                {"name": "test-onto", "resources": [{"name": "ImageResource", "super": "StillImageRepresentation"}]}
            ],
        }
    }


@pytest.fixture
def project_invalid_format() -> dict[str, Any]:
    """Project with invalid class reference format"""
    return {
        "project": {
            "shortcode": "1234",
            "shortname": "test-project",
            "default_permissions_overrule": {"limited_view": ["InvalidFormat"]},
            "ontologies": [
                {"name": "test-onto", "resources": [{"name": "ImageResource", "super": "StillImageRepresentation"}]}
            ],
        }
    }


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


def test_check_overrule_no_overrule(project_no_overrule: dict[str, Any]) -> None:
    """Test that validation passes when no default_permissions_overrule exists"""
    assert _check_for_invalid_default_permissions_overrule(project_no_overrule) is True


def test_check_overrule_no_limited_view(project_no_limited_view: dict[str, Any]) -> None:
    """Test that validation passes when no limited_view exists"""
    assert _check_for_invalid_default_permissions_overrule(project_no_limited_view) is True


def test_check_overrule_valid_direct_inheritance(project_valid_direct_inheritance: dict[str, Any]) -> None:
    """Test that validation passes for direct inheritance from StillImageRepresentation"""
    assert _check_for_invalid_default_permissions_overrule(project_valid_direct_inheritance) is True


def test_check_overrule_valid_indirect_inheritance(project_valid_indirect_inheritance: dict[str, Any]) -> None:
    """Test that validation passes for indirect inheritance through another resource"""
    assert _check_for_invalid_default_permissions_overrule(project_valid_indirect_inheritance) is True


def test_check_overrule_valid_multiple_inheritance(project_valid_multiple_inheritance: dict[str, Any]) -> None:
    """Test that validation passes for multiple inheritance (list format)"""
    assert _check_for_invalid_default_permissions_overrule(project_valid_multiple_inheritance) is True


def test_check_overrule_valid_cross_ontology_inheritance(project_cross_ontology_inheritance: dict[str, Any]) -> None:
    """Test that validation passes for cross-ontology inheritance"""
    assert _check_for_invalid_default_permissions_overrule(project_cross_ontology_inheritance) is True


def test_check_overrule_invalid_wrong_superclass(project_invalid_wrong_superclass: dict[str, Any]) -> None:
    """Test that validation fails for wrong superclass"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_invalid_wrong_superclass)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "PDFResource" in error_message
    assert "directly or through inheritance" in error_message


def test_check_overrule_invalid_missing_resource(project_invalid_missing_resource: dict[str, Any]) -> None:
    """Test that validation fails for non-existent resource"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_invalid_missing_resource)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "NonExistentResource" in error_message
    assert "not found in ontology" in error_message


def test_check_overrule_invalid_missing_ontology(project_invalid_missing_ontology: dict[str, Any]) -> None:
    """Test that validation fails for non-existent ontology"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_invalid_missing_ontology)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "nonexistent-onto" in error_message
    assert "not found" in error_message


def test_check_overrule_invalid_format(project_invalid_format: dict[str, Any]) -> None:
    """Test that validation fails for invalid class reference format"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_invalid_format)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "InvalidFormat" in error_message
    assert "Invalid format, expected 'ontology:ClassName'" in error_message


def test_check_overrule_circular_reference(project_circular_reference: dict[str, Any]) -> None:
    """Test that validation handles circular references gracefully"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_circular_reference)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "Resource1" in error_message
    assert "directly or through inheritance" in error_message


def test_check_overrule_mixed_valid_invalid(project_mixed_valid_invalid: dict[str, Any]) -> None:
    """Test validation with mixed valid and invalid classes"""
    with pytest.raises(BaseError) as exc_info:
        _check_for_invalid_default_permissions_overrule(project_mixed_valid_invalid)

    error_message = str(exc_info.value)
    assert "must be subclasses of 'StillImageRepresentation'" in error_message
    assert "PDFResource" in error_message
    # Should not mention the valid classes
    assert "ImageResource" not in error_message or "Class reference 'test-onto:ImageResource'" not in error_message
    assert (
        "SubImageResource" not in error_message or "Class reference 'test-onto:SubImageResource'" not in error_message
    )


def test_check_overrule_limited_view_all(project_limited_view_all: dict[str, Any]) -> None:
    """Test that validation passes when limited_view is 'all'"""
    assert _check_for_invalid_default_permissions_overrule(project_limited_view_all)
