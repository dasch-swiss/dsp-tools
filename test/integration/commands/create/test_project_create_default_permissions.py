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

STILL_IMAGE_IRI = f"{ONTO_NAMESPACE_STR}ImageResource"
MOVING_IMAGE_IRI = f"{ONTO_NAMESPACE_STR}VideoResource"
AUDIO_IRI = f"{ONTO_NAMESPACE_STR}AudioResource"

_KNORA_API = "http://api.knora.org/ontology/knora-api/v2#"
_STILL_IMAGE_FILE_VALUE = f"{_KNORA_API}hasStillImageFileValue"
_MOVING_IMAGE_FILE_VALUE = f"{_KNORA_API}hasMovingImageFileValue"
_AUDIO_FILE_VALUE = f"{_KNORA_API}hasAudioFileValue"
_ALL_FILE_VALUE_PROPS = {_STILL_IMAGE_FILE_VALUE, _MOVING_IMAGE_FILE_VALUE, _AUDIO_FILE_VALUE}


@pytest.fixture
def mock_permissions_client() -> MagicMock:
    mock_client = MagicMock()
    mock_client.project_iri = "http://rdfh.ch/projects/test-project"
    mock_client.auth = MagicMock()
    mock_client.auth.server = "http://0.0.0.0:3333"

    mock_client.get_project_doaps.return_value = [{"iri": "http://test.iri/existing-doap"}]
    mock_client.delete_doap.return_value = True
    mock_client.create_new_doap.return_value = True
    return mock_client


@pytest.fixture
def created_iris() -> CreatedIriCollection:
    return CreatedIriCollection(created_classes={STILL_IMAGE_IRI, MOVING_IMAGE_IRI, AUDIO_IRI})


def test_create_default_permissions_with_limited_view_all(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
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
    calls = mock_permissions_client.create_new_doap.call_args_list

    # Find the limited view DOAP calls (those with forProperty set to a file value prop)
    limited_view_calls = [c[0][0] for c in calls if c[0][0].get("forProperty") in _ALL_FILE_VALUE_PROPS]

    # There must be exactly 3 DOAPs: one per file value property
    assert len(limited_view_calls) == 3, f"Expected 3 limited_view DOAPs, got {len(limited_view_calls)}"
    props_used = {c["forProperty"] for c in limited_view_calls}
    assert props_used == _ALL_FILE_VALUE_PROPS

    for call in limited_view_calls:
        assert call["forResourceClass"] is None
        assert call["forProject"] == "http://rdfh.ch/projects/test-project"
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
        assert call["hasPermissions"] == expected_permissions


def test_create_default_permissions_with_limited_view_specific_classes(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    limited_view = LimitedViewPermissionsSelection(
        limited_selection=[STILL_IMAGE_IRI, MOVING_IMAGE_IRI, AUDIO_IRI],
        still_image=[STILL_IMAGE_IRI],
        moving_image=[MOVING_IMAGE_IRI],
        audio=[AUDIO_IRI],
    )

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=limited_view,
        ),
        created_iris=created_iris,
    )

    assert result is True

    calls = mock_permissions_client.create_new_doap.call_args_list
    limited_view_calls = [c[0][0] for c in calls if c[0][0].get("forProperty") in _ALL_FILE_VALUE_PROPS]

    assert len(limited_view_calls) == 3, f"Expected 3 limited_view DOAPs, got {len(limited_view_calls)}"

    prop_to_class = {c["forProperty"]: c["forResourceClass"] for c in limited_view_calls}
    assert prop_to_class[_STILL_IMAGE_FILE_VALUE] == STILL_IMAGE_IRI
    assert prop_to_class[_MOVING_IMAGE_FILE_VALUE] == MOVING_IMAGE_IRI
    assert prop_to_class[_AUDIO_FILE_VALUE] == AUDIO_IRI


def test_create_default_permissions_with_limited_view_still_image_only(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
    limited_view = LimitedViewPermissionsSelection(
        limited_selection=[STILL_IMAGE_IRI],
        still_image=[STILL_IMAGE_IRI],
        moving_image=[],
        audio=[],
    )

    result = create_default_permissions(
        perm_client=mock_permissions_client,
        parsed_permissions=ParsedPermissions(
            default_permissions=DefaultPermissions.PUBLIC,
            overrule_private=None,
            overrule_limited_view=limited_view,
        ),
        created_iris=created_iris,
    )

    assert result is True

    calls = mock_permissions_client.create_new_doap.call_args_list
    limited_view_calls = [c[0][0] for c in calls if c[0][0].get("forProperty") in _ALL_FILE_VALUE_PROPS]

    assert len(limited_view_calls) == 1
    assert limited_view_calls[0]["forProperty"] == _STILL_IMAGE_FILE_VALUE
    assert limited_view_calls[0]["forResourceClass"] == STILL_IMAGE_IRI


def test_create_default_permissions_no_overrule(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
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
    assert mock_permissions_client.create_new_doap.call_count == 1
    call = mock_permissions_client.create_new_doap.call_args_list[0]
    payload = call[0][0]
    assert "forProperty" not in payload
    assert "forResourceClass" not in payload
    assert payload["forProject"] == "http://rdfh.ch/projects/test-project"


def test_create_default_permissions_get_doaps_failure(
    mock_permissions_client: MagicMock, created_iris: CreatedIriCollection
) -> None:
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
