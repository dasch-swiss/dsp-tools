from dataclasses import dataclass, field
from typing import Any

from dsp_tools.connection.connection import Connection
from dsp_tools.utils.xmlupload.stash.stash_models import LinkValueStash, LinkValueStashItem, StandoffStash, Stash
from dsp_tools.utils.xmlupload.xmlupload import _upload_stash

# pylint: disable=unused-argument,missing-function-docstring


@dataclass
class ConnectionMock:
    """Mock class for Connection."""

    get_responses: list[dict[str, Any]] = field(default_factory=list)
    post_responses: list[dict[str, Any]] = field(default_factory=list)

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
        raise AssertionError("'put' not implemented")

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
            standoff_stash=StandoffStash.make([]),
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
        con: Connection = ConnectionMock(
            get_responses=[{"@context": {}}],  # TODO: this should not be needed
            post_responses=[{}],
        )
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            verbose=False,
        )
        assert nonapplied is None

    def test_not_upload_link_value_stash_without_res_id(self) -> None:
        """Do not upload stashed link values, if a resource ID cannot be resolved to an IRI."""
        stash = Stash.make(
            standoff_stash=StandoffStash.make([]),
            link_value_stash=LinkValueStash.make(
                [
                    LinkValueStashItem("001", "sometype", "someprop", "002"),
                ],
            ),
        )
        assert stash
        id2iri_mapping = {
            "002": "http://www.rdfh.ch/0001/002",
        }
        con: Connection = ConnectionMock(
            get_responses=[{"@context": {}}],  # TODO: this should not be needed
            post_responses=[{}],
        )
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            verbose=False,
        )
        assert nonapplied

    def test_not_upload_link_value_stash_without_target_id(self) -> None:
        """Do not upload stashed link values, if a target ID cannot be resolved to an IRI."""
        stash = Stash.make(
            standoff_stash=StandoffStash.make([]),
            link_value_stash=LinkValueStash.make(
                [
                    LinkValueStashItem("001", "sometype", "someprop", "002"),
                ],
            ),
        )
        assert stash
        id2iri_mapping = {
            "001": "http://www.rdfh.ch/0001/001",
        }
        con: Connection = ConnectionMock(
            get_responses=[{"@context": {}}],  # TODO: this should not be needed
            post_responses=[{}],
        )
        nonapplied = _upload_stash(
            stash=stash,
            id2iri_mapping=id2iri_mapping,
            con=con,
            verbose=False,
        )
        assert nonapplied
