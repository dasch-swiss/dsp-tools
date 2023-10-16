from typing import Any, Protocol


class Connection(Protocol):
    """
    Protocol class/interface for the connection object.

    Exposes:
        - get
        - put
        - post
        - delete
    """

    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            headers: headers for the HTTP request
        """

    def put(
        self,
        route: str,
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']
        """

    def post(
        self,
        route: str,
        jsondata: str | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']
        """

    def delete(
        self,
        route: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            params: additional parameters for the HTTP request
        """

    def get_token(self) -> str:
        """
        Return the token of this connection.

        Raises:
            BaseError: if no token is available
        """
