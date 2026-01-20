from unittest.mock import MagicMock

import pytest

from dsp_tools.commands.create.create_on_server.default_permissions import create_default_permissions
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewPermissionsSelection
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR


@pytest.fixture
def mock_permissions_client() -> MagicMock:
    """Create a mock PermissionsClient."""
    mock_client = MagicMock()
    mock_client.project_iri = "http://rdfh.ch/projects/test-project"
    mock_client.auth = MagicMock()
    mock_client.auth.server = "http://0.0.0.0:3333"

    # Mock successful API calls
    # Return a list with some existing DOAPs to avoid the logic issue in _delete_existing_doaps
    mock_client.get_project_doaps.return_value = [{"iri": "http://test.iri/existing-doap"}]
    mock_client.delete_doap.return_value = True
    mock_client.create_new_doap.return_value = True
    return mock_client


@pytest.fixture
def created_iris() -> CreatedIriCollection:
    return CreatedIriCollection(
        created_classes={f"{ONTO_NAMESPACE_STR}ImageResource", f"{ONTO_NAMESPACE_STR}PhotoResource"}
    )


def test_create_default_permissions_with_limited_view_all(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    """Test that limited_view: 'all' creates a DOAP without class restriction."""

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=GlobalLimitedViewPermission.ALL,
        ),
        created_iris=created_iris,
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


def test_create_default_permissions_with_limited_view_specific_classes(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    limited_view_iris = [f"{ONTO_NAMESPACE_STR}ImageResource", f"{ONTO_NAMESPACE_STR}PhotoResource"]

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=LimitedViewPermissionsSelection(limited_view_iris),
        ),
        created_iris=created_iris,
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
    assert set(resource_class_iris) == set(limited_view_iris)


def test_create_default_permissions_no_overrule(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    """Test that default permissions work without any overrules."""
    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=GlobalLimitedViewPermission.NONE,
        ),
        created_iris=created_iris,
    )

    assert result is True

    # Should only create the basic default DOAP, no overrule DOAPs
    assert mock_permissions_client.create_new_doap.call_count == 1
    call = mock_permissions_client.create_new_doap.call_args_list[0]
    payload = call[0][0]
    assert "forProperty" not in payload  # Basic DOAP doesn't specify property
    assert "forResourceClass" not in payload  # Basic DOAP doesn't specify resource class
    assert payload["forProject"] == "http://rdfh.ch/projects/test-project"


def test_create_default_permissions_get_doaps_failure(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    """Test handling of get_project_doaps failures."""
    mock_permissions_client.get_project_doaps.return_value = ResponseCodeAndText(500, "Internal error")
    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=GlobalLimitedViewPermission.ALL,
        ),
        created_iris=created_iris,
    )
    assert result is False


def test_create_default_permissions_delete_doap_failure(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    """Test handling of delete_doap failures."""
    mock_permissions_client.delete_doap.side_effect = BadCredentialsError("No permission")
    with pytest.raises(BadCredentialsError):
        create_default_permissions(
            perm_client=mock_permissions_client,
            parsed_permissions=ParsedPermissions(
                default_permissions=DefaultPermissions.PUBLIC,
                overrule_private=None,
                overrule_limited_view=GlobalLimitedViewPermission.ALL,
            ),
            created_iris=created_iris,
        )


def test_create_default_permissions_create_doap_failure(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    """Test handling of create_new_doap failures (returns ResponseCodeAndText on error)."""
    mock_permissions_client.create_new_doap.return_value = ResponseCodeAndText(400, "Bad request")
    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=GlobalLimitedViewPermission.ALL,
        ),
        created_iris=created_iris,
    )

    assert result is False
