from typing import Any
from typing import Protocol

from dsp_tools.utils.request_utils import PostFiles


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
        files: PostFiles | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        pass
