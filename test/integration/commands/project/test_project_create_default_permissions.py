from unittest.mock import MagicMock

import pytest

from dsp_tools.commands.project.create.project_create_default_permissions import create_default_permissions


@pytest.fixture
def mock_permissions_client() -> MagicMock:
    """Create a mock PermissionsClient."""
    mock_client = MagicMock()
    mock_client.proj_iri = "http://rdfh.ch/projects/test-project"
    mock_client.auth = MagicMock()
    mock_client.auth.server = "https://api.dev.dasch.swiss"

    # Mock successful API calls
    # Return a list with some existing DOAPs to avoid the logic issue in _delete_existing_doaps
    mock_client.get_project_doaps.return_value = [{"iri": "http://test.iri/existing-doap"}]
    mock_client.delete_doap.return_value = True
    mock_client.create_new_doap.return_value = True

    return mock_client


def test_create_default_permissions_with_limited_view_all(mock_permissions_client: MagicMock) -> None:
    """Test that limited_view: 'all' creates a DOAP without class restriction."""
    default_permissions_overrule: dict[str, str | list[str]] = {"private": [], "limited_view": "all"}

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        default_permissions="public",
        default_permissions_overrule=default_permissions_overrule,
        shortcode="1234",
    )

    assert result is True
    assert mock_permissions_client.create_new_doap.call_count >= 1
    calls = mock_permissions_client.create_new_doap.call_args_list

    # Find the call for the limited view DOAP (should have forProperty and forResourceClass: None)
    limited_view_call = None
    for call in calls:
        payload = call[0][0]  # First argument is the payload
        if payload.get("forProperty") == "http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue":
            limited_view_call = payload
            break

    assert limited_view_call is not None, "Expected a DOAP call for hasStillImageFileValue property"

    # Verify the DOAP structure for limited_view: "all"
    assert limited_view_call["forProperty"] == "http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue"
    assert limited_view_call["forResourceClass"] is None  # This is the key requirement
    assert limited_view_call["forProject"] == "http://rdfh.ch/projects/test-project"

    # Verify the permissions structure
    expected_permissions = [
        {
            "additionalInformation": "http://www.knora.org/ontology/knora-admin#ProjectAdmin",
            "name": "CR",
            "permissionCode": None,
        },
        {
            "additionalInformation": "http://www.knora.org/ontology/knora-admin#ProjectMember",
            "name": "D",
            "permissionCode": None,
        },
        {
            "additionalInformation": "http://www.knora.org/ontology/knora-admin#KnownUser",
            "name": "RV",
            "permissionCode": None,
        },
        {
            "additionalInformation": "http://www.knora.org/ontology/knora-admin#UnknownUser",
            "name": "RV",
            "permissionCode": None,
        },
    ]
    assert limited_view_call["hasPermissions"] == expected_permissions


def test_create_default_permissions_with_limited_view_specific_classes(mock_permissions_client: MagicMock) -> None:
    default_permissions_overrule: dict[str, str | list[str]] = {
        "private": [],
        "limited_view": ["test-onto:ImageResource", "test-onto:PhotoResource"],
    }

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        default_permissions="public",
        default_permissions_overrule=default_permissions_overrule,
        shortcode="1234",
    )

    assert result is True

    # Verify that create_new_doap was called multiple times (base + 2 limited view overrules)
    calls = mock_permissions_client.create_new_doap.call_args_list

    # Find calls for the limited view DOAPs (should have forResourceClass with specific IRIs)
    limited_view_calls = []
    for call in calls:
        payload = call[0][0]
        if payload.get("forProperty") == "http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue":
            limited_view_calls.append(payload)

    assert len(limited_view_calls) == 2, "Expected 2 DOAP calls for 2 specific image classes"

    # Verify that both calls have specific resource class IRIs (not None)
    resource_class_iris = [call["forResourceClass"] for call in limited_view_calls]
    expected_iris = [
        "http://api.dev.dasch.swiss/ontology/1234/test-onto/v2#ImageResource",
        "http://api.dev.dasch.swiss/ontology/1234/test-onto/v2#PhotoResource",
    ]

    assert set(resource_class_iris) == set(expected_iris)


def test_create_default_permissions_no_overrule(mock_permissions_client: MagicMock) -> None:
    """Test that default permissions work without any overrules."""
    result = create_default_permissions(
        perm_client=mock_permissions_client,
        default_permissions="public",
        default_permissions_overrule=None,
        shortcode="1234",
    )

    assert result is True

    # Should only create the basic default DOAP, no overrule DOAPs
    assert mock_permissions_client.create_new_doap.call_count == 1
    call = mock_permissions_client.create_new_doap.call_args_list[0]
    payload = call[0][0]
    assert "forProperty" not in payload  # Basic DOAP doesn't specify property
    assert "forResourceClass" not in payload  # Basic DOAP doesn't specify resource class
    assert payload["forProject"] == "http://rdfh.ch/projects/test-project"


def test_create_default_permissions_api_failure(mock_permissions_client: MagicMock) -> None:
    """Test handling of API failures."""
    # Mock API failure
    mock_permissions_client.create_new_doap.return_value = False

    default_permissions_overrule: dict[str, str | list[str]] = {"private": [], "limited_view": "all"}

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        default_permissions="public",
        default_permissions_overrule=default_permissions_overrule,
        shortcode="1234",
    )

    assert result is False
