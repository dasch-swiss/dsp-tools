from dataclasses import dataclass
from typing import Any

from dsp_tools.connection.connection import Connection
from dsp_tools.utils.xmlupload.stash.stash_models import LinkValueStash, StandoffStash, Stash
from dsp_tools.utils.xmlupload.xmlupload import _upload_stash


@dataclass
class ConnectionMock:
    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return {}

    def put(
        self,
        route: str,
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        return {}

    def post(
        self,
        route: str,
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        return {}

    def delete(
        self,
        route: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {}

    def get_token(self) -> str:
        return "..."

    def login(self, email: str, password: str) -> None:
        return

    def logout(self) -> None:
        return


def test_foobar() -> None:
    stash = Stash.make(
        standoff_stash=StandoffStash(
            res_2_stash_items={},
            res_2_xmlres={},
        ),
        link_value_stash=LinkValueStash.make(
            [],
        ),
    )
    assert stash
    con: Connection = ConnectionMock()
    _ = _upload_stash(
        stash=stash,
        id2iri_mapping={},
        con=con,
        verbose=False,
    )
    assert True
