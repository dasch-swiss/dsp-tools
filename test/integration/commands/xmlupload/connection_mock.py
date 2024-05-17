from dataclasses import dataclass
from typing import Any

import pytest

from dsp_tools.utils.connection import Connection

# ruff: noqa: ARG002 (unused-method-argument)


@dataclass
class ConnectionMockBase(Connection):
    """
    Base mock for the Connection class.
    Does not have any capabilities, but subclasses can override methods.
    """

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        raise AssertionError("GET not implemented in mock")

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        raise AssertionError("PUT not implemented in mock")

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        raise AssertionError("POST not implemented in mock")

    def delete(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        raise AssertionError("DELETE not implemented in mock")

    def get_token(self) -> str:
        raise AssertionError("get_token not implemented in mock")

    def login(self, email: str, password: str) -> None:
        raise AssertionError("login not implemented in mock")

    def logout(self) -> None:
        raise AssertionError("logout not implemented in mock")


if __name__ == "__main__":
    pytest.main([__file__])
