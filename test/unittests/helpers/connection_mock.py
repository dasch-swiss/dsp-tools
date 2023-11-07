from dataclasses import dataclass
from typing import Any

# pylint: disable=missing-class-docstring,missing-function-docstring,unused-argument


@dataclass
class ConnectionMockBase:
    """
    Base mock for the Connection class.
    Does not have any capabilities but subclasses can override methods.
    """

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        raise NotImplementedError("GET not implemented in mock")

    def put(self, route: str, jsondata: str | None = None, content_type: str = "application/json") -> dict[str, Any]:
        raise NotImplementedError("PUT not implemented in mock")

    def post(self, route: str, jsondata: str | None = None, content_type: str = "application/json") -> dict[str, Any]:
        raise NotImplementedError("POST not implemented in mock")

    def delete(self, route: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError("DELETE not implemented in mock")

    def get_token(self) -> str:
        raise NotImplementedError("get_token not implemented in mock")

    def login(self, email: str, password: str) -> None:
        raise NotImplementedError("login not implemented in mock")
