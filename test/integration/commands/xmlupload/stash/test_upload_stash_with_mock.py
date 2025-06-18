# mypy: disable-error-code="method-assign,no-untyped-def"

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from uuid import uuid4

import pytest

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _upload_stash
from dsp_tools.utils.request_utils import PostFiles
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase

# ruff: noqa: ARG002 (unused-method-argument)

SOME_PROP_STR = "http://0.0.0.0:3333/ontology/4123/testonto/v2#someprop"


@dataclass
class ProjectClientStub:
    """Stub class for ProjectClient."""

    con: Connection
    shortcode: str
    project_info: ProjectInfo | None

    def get_project_iri(self) -> str:
        raise NotImplementedError("get_project_iri not implemented")

    def get_ontology_iris(self) -> list[str]:
        raise NotImplementedError("get_project_iri not implemented")

    def get_ontology_name_dict(self) -> dict[str, str]:
        return {}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        raise NotImplementedError("get_project_iri not implemented")


@dataclass
class ConnectionMock(ConnectionMockBase):
    """Mock class for Connection."""

    get_responses: list[dict[str, Any]] = field(default_factory=list)
    post_responses: list[dict[str, Any]] = field(default_factory=list)
    put_responses: list[dict[str, Any]] = field(default_factory=list)

    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.get_responses.pop(0)

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: PostFiles | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        return self.post_responses.pop(0)

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return self.put_responses.pop(0)


@pytest.fixture
def link_val_stash_target_id_2():
    val = ProcessedLink("002", SOME_PROP_STR, None, None, str(uuid4()))
    return LinkValueStashItem("001", "sometype", val)


class TestUploadLinkValueStashes:
    def test_upload_link_value_stash(self, link_val_stash_target_id_2: LinkValueStashItem) -> None:
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
        con: Connection = ConnectionMock(post_responses=[{}])
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        _upload_stash(upload_state, ProjectClientStub(con, "1234", None))
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()

    def test_upload_link_value_stash_multiple(self, link_val_stash_target_id_2: LinkValueStashItem) -> None:
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
        con: Connection = ConnectionMock(post_responses=[{}, {}, {}, {}])
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        _upload_stash(upload_state, ProjectClientStub(con, "1234", None))
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()


class TestUploadTextValueStashes:
    def test_upload_text_value_stash(self) -> None:
        """Upload stashed text values (standoff), if all goes well."""
        value_uuid = str(uuid4())
        property_name = SOME_PROP_STR
        val = ProcessedRichtext(
            value=FormattedTextValue("<p>some text</p>"),
            prop_iri=property_name,
            value_uuid=value_uuid,
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
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    "testonto:someprop": [
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": "<p>not relevant</p>",
                        },
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": f"<p>{value_uuid}</p>",
                        },
                    ],
                    "@context": {},
                },
            ],
            put_responses=[{}],
        )
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        _upload_stash(upload_state, ProjectClientStub(con, "1234", None))
        assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()

    def test_not_upload_text_value_stash_if_uuid_not_on_value(self) -> None:
        """
        Do not upload stashed text values (standoff), if the resource has no value containing the UUID of the stashed
        text value in its text.
        """
        value_uuid = str(uuid4())
        property_name = SOME_PROP_STR
        val = ProcessedRichtext(
            value=FormattedTextValue("<p>some text</p>"),
            prop_iri=property_name,
            value_uuid=value_uuid,
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
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    "testonto:someprop": [
                        {
                            "@id": "http://www.rdfh.ch/0001/001/values/01",
                            "knora-api:textValueAsXml": "<p>not relevant</p>",
                        },
                    ],
                    "@context": {},
                },
            ],
            put_responses=[{}],
        )
        upload_state = UploadState([], stash, UploadConfig(), [], iri_resolver)
        _upload_stash(upload_state, ProjectClientStub(con, "1234", None))
        assert upload_state.pending_stash == stash
