from dataclasses import dataclass
from typing import Any

# pylint: disable=unused-argument
# ruff: noqa: D102 (undocumented-public-method)


@dataclass
class ConnectionMockBase:
    """
    Base mock for the Connection class.
    Does not have any capabilities but subclasses can override methods.
    """

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        raise AssertionError("GET not implemented in mock")

    def put(self, route: str, jsondata: str | None = None, content_type: str = "application/json") -> dict[str, Any]:
        raise AssertionError("PUT not implemented in mock")

    def post(self, route: str, jsondata: str | None = None, content_type: str = "application/json") -> dict[str, Any]:
        raise AssertionError("POST not implemented in mock")

    def delete(self, route: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        raise AssertionError("DELETE not implemented in mock")

    def get_token(self) -> str:
        raise AssertionError("get_token not implemented in mock")

    def login(self, email: str, password: str) -> None:
        raise AssertionError("login not implemented in mock")

    def logout(self) -> None:
        raise AssertionError("logout not implemented in mock")
