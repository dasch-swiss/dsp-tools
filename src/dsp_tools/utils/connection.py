from typing import Any
from typing import Protocol


class Connection(Protocol):
    """
    Protocol class/interface for the connection object.
    """

    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        pass

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        pass

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        pass

    def delete(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        pass

    def get_token(self) -> str:
        pass

    def login(self, email: str, password: str) -> None:
        pass

    def logout(self) -> None:
        pass
