from unittest.mock import Mock
from unittest.mock import create_autospec
from unittest.mock import patch
from uuid import uuid4

import pytest

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.clients.value_client_live import ValueClientLive
from dsp_tools.commands.xmlupload.execute_upload import _upload_stash
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig

SOME_PROP_STR = "http://0.0.0.0:3333/ontology/4123/testonto/v2#someprop"
LOCALHOST = "http://0.0.0.0:3333"
VALUE_UUID = str(uuid4())


@pytest.fixture
def auth() -> AuthenticationClient:
    mock_auth = Mock(spec_set=AuthenticationClient)
    mock_auth.get_token = Mock(return_value="tkn")
    return mock_auth


@pytest.fixture
def resource_client(auth) -> ResourceClientLive:
    mock_resource_client: ResourceClientLive = create_autospec(ResourceClientLive, instance=True)
    mock_resource_client.server = LOCALHOST
    mock_resource_client.auth = auth
    return mock_resource_client


@pytest.fixture
def link_val_stash_target_id_2():
    val = ProcessedLink("002", SOME_PROP_STR, None, None, str(uuid4()))
    return LinkValueStashItem("001", "sometype", val)


class TestUploadLinkValueStashes:
    def test_upload_link_value_stash(self, link_val_stash_target_id_2: LinkValueStashItem, resource_client) -> None:
        """Upload stashed link values (resptr), if all goes well."""
        stash = Stash.make(
            standoff_stash=None,
            link_value_stash=LinkValueStash.make(
                [link_val_stash_target_id_2],
            ),
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )

        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        with patch.object(ValueClientLive, "post_new_value", return_value=None):
            _upload_stash(upload_state, resource_client)
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()

    def test_upload_link_value_stash_multiple(
        self, link_val_stash_target_id_2: LinkValueStashItem, resource_client
    ) -> None:
        """Upload multiple stashed link values (resptr), if all goes well."""
        stash = Stash.make(
            standoff_stash=None,
            link_value_stash=LinkValueStash.make(
                [
                    link_val_stash_target_id_2,
                    LinkValueStashItem(
                        "001", "sometype", ProcessedLink("003", SOME_PROP_STR, None, None, str(uuid4()))
                    ),
                    LinkValueStashItem(
                        "002", "sometype", ProcessedLink("003", SOME_PROP_STR, None, None, str(uuid4()))
                    ),
                    LinkValueStashItem(
                        "004", "sometype", ProcessedLink("002", SOME_PROP_STR, None, None, str(uuid4()))
                    ),
                ],
            ),
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
                "003": "http://www.rdfh.ch/0001/003",
                "004": "http://www.rdfh.ch/0001/004",
            }
        )
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        with patch.object(ValueClientLive, "post_new_value", return_value=None):
            _upload_stash(upload_state, resource_client)
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()


class TestUploadTextValueStashes:
    def test_upload_text_value_stash(self, resource_client) -> None:
        """Upload stashed text values (standoff), if all goes well."""
        property_name = SOME_PROP_STR
        val = ProcessedRichtext(
            value=FormattedTextValue("<p>some text</p>"),
            prop_iri=property_name,
            value_uuid=VALUE_UUID,
            resource_references=set(),
            permissions=None,
            comment=None,
        )
        stash = Stash.make(
            standoff_stash=StandoffStash.make([StandoffStashItem("001", "sometype", val)]), link_value_stash=None
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )
        resource_client.get_resource.return_value = {
            "testonto:someprop": [
                {
                    "@id": "http://www.rdfh.ch/0001/001/values/01",
                    "knora-api:textValueAsXml": "<p>not relevant</p>",
                },
                {
                    "@id": "http://www.rdfh.ch/0001/001/values/02",
                    "knora-api:textValueAsXml": f"<p>{VALUE_UUID}</p>",
                },
            ],
            "@context": {},
        }
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        with patch.object(ValueClientLive, "replace_existing_value", return_value=None):
            _upload_stash(upload_state, resource_client)
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()

    def test_not_upload_text_value_stash_if_uuid_not_on_value(self, resource_client) -> None:
        """
        Do not upload stashed text values (standoff), if the resource has no value containing the UUID of the stashed
        text value in its text.
        """
        property_name = SOME_PROP_STR
        val = ProcessedRichtext(
            value=FormattedTextValue("<p>some text</p>"),
            prop_iri=property_name,
            value_uuid=VALUE_UUID,
            resource_references=set(),
            permissions=None,
            comment=None,
        )
        stash = Stash.make(
            standoff_stash=StandoffStash.make([StandoffStashItem("001", "sometype", val)]), link_value_stash=None
        )
        assert stash
        iri_resolver = IriResolver(
            {
                "001": "http://www.rdfh.ch/0001/001",
                "002": "http://www.rdfh.ch/0001/002",
            }
        )
        resource_client.get_resource.return_value = {
            "testonto:someprop": [
                {
                    "@id": "http://www.rdfh.ch/0001/001/values/01",
                    "knora-api:textValueAsXml": "<p>not relevant</p>",
                },
            ],
            "@context": {},
        }
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        with patch.object(ValueClientLive, "replace_existing_value", return_value=None):
            _upload_stash(upload_state, resource_client)
        assert upload_state.pending_stash == stash
