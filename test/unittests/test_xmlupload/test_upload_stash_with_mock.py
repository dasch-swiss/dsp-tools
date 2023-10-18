from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from dsp_tools.connection.connection import Connection
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.utils.xmlupload.stash.stash_models import (
    LinkValueStash,
    LinkValueStashItem,
    StandoffStash,
    StandoffStashItem,
    Stash,
)
from dsp_tools.utils.xmlupload.xmlupload import _upload_stash

# pylint: disable=unused-argument,missing-function-docstring,missing-class-docstring,too-few-public-methods


@dataclass
class ConnectionMock:
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
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        return self.post_responses.pop(0)

    def put(
        self,
        route: str,
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        return self.put_responses.pop(0)

    def delete(
        self,
        route: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise AssertionError("'delete' not implemented")

    def get_token(self) -> str:
        raise AssertionError("'get token' not implemented in this mock")

    def login(self, email: str, password: str) -> None:
        raise AssertionError("'login' not implemented in this mock")

    def logout(self) -> None:
        raise AssertionError("'logout' not implemented in this mock")


class TestUploadLinkValueStashes:
    def test_upload_link_value_stash(self) -> None:
        """Upload stashed link values (resptr), if all goes well."""
        stash = Stash.make(
            standoff_stash=None,
            link_value_stash=LinkValueStash.make(
                [
                    LinkValueStashItem("001", "sometype", "someprop", "002"),
                ],
            ),
        )
        assert stash
        id2iri_mapping = {
            "001": "http://www.rdfh.ch/0001/001",
            "002": "http://www.rdfh.ch/0001/002",
        }
        con: Connection = ConnectionMock(post_responses=[{}])
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            context={},
            verbose=False,
        )
        assert nonapplied is None


class TestUploadTextValueStashes:
    def test_upload_text_value_stash(self) -> None:
        """Upload stashed text values (standoff), if all goes well."""
        value_uuid = str(uuid4())
        property_name = "someprop"
        stash = Stash.make(
            standoff_stash=StandoffStash.make(
                [
                    StandoffStashItem(
                        "001", "sometype", value_uuid, property_name, KnoraStandoffXml("<p>some text</p>")
                    ),
                ]
            ),
            link_value_stash=None,
        )
        assert stash
        id2iri_mapping = {
            "001": "http://www.rdfh.ch/0001/001",
            "002": "http://www.rdfh.ch/0001/002",
        }
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    property_name: [
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
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            context={},
            verbose=False,
        )
        assert nonapplied is None

    def test_not_upload_text_value_stash_if_uuid_not_on_value(self) -> None:
        """
        Do not upload stashed text values (standoff), if the resource has no value containing the UUID of the stashed
        text value in its text.
        """
        value_uuid = str(uuid4())
        property_name = "someprop"
        stash = Stash.make(
            standoff_stash=StandoffStash.make(
                [
                    StandoffStashItem(
                        "001", "sometype", value_uuid, property_name, KnoraStandoffXml("<p>some text</p>")
                    ),
                ]
            ),
            link_value_stash=None,
        )
        assert stash
        id2iri_mapping = {
            "001": "http://www.rdfh.ch/0001/001",
            "002": "http://www.rdfh.ch/0001/002",
        }
        con: Connection = ConnectionMock(
            get_responses=[
                {
                    property_name: [
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
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            context={},
            verbose=False,
        )
        assert nonapplied == stash
