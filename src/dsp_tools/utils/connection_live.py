import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, cast

import requests

from dsp_tools.models.exceptions import BaseError


def check_for_api_error(response: requests.Response) -> None:
    """
    Check the response of an API request if it contains an error raised by DSP-API.

    Args:
        response: The requests.Response object that is returned by the API request

    Raises:
        BaseError: If the status code of the response is not 200
    """
    if response.status_code != 200:
        raise BaseError(
            message=f"KNORA-ERROR: status code={response.status_code}\nMessage: {response.text}",
            status_code=response.status_code,
            json_content_of_api_response=response.text,
            reason_from_api=response.reason,
            api_route=response.url,
        )


@dataclass
class ConnectionLive:
    """
    A Connection instance represents a connection to a DSP server.

    Attributes:
        server: address of the server, e.g https://api.dasch.swiss
        dump: if True, every request is written into a file
        dump_directory: directory where the HTTP requests are written
        token: session token received by the server after login
    """

    server: str
    dump: bool = False
    dump_directory = Path("HTTP requests")
    token: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Create dumping directory (if applicable).

        Raises:
            BaseError: if DSP-API returns no token with the provided user credentials
        """
        if self.dump:
            self.dump_directory.mkdir(exist_ok=True)

    def login(self, email: str, password: str) -> None:
        """
        Retrieve a session token and store it as class attribute.

        Args:
            email: email address of the user
            password: password of the user

        Raises:
            BaseError: if DSP-API returns no token with the provided user credentials
        """
        response = self.post(
            route="/v2/authentication",
            jsondata=json.dumps({"email": email, "password": password}),
        )
        if not response.get("token"):
            raise BaseError(
                f"Error when trying to login with user '{email}' and password '{password} "
                f"on server '{self.server}'",
                json_content_of_api_response=json.dumps(response),
                api_route="/v2/authentication",
            )
        self.token = response["token"]

    def logout(self) -> None:
        """
        Delete the token on the server and in this class.
        """
        if self.token:
            self.delete(route="/v2/authentication")
            self.token = None

    def get_token(self) -> str:
        """
        Return the token of this connection.

        Returns:
            token

        Raises:
            BaseError: if no token is available
        """
        if not self.token:
            raise BaseError("No token available.")
        return self.token

    def _write_request_to_file(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        jsondata: Optional[str],
        params: Optional[dict[str, Any]],
        response: requests.Response,
    ) -> None:
        """
        Write the request and response to a file.

        Args:
            method: HTTP method (POST, GET, PUT, DELETE)
            url: complete URL (server + route of DSP-API) that was called
            headers: headers of the HTTP request
            jsondata: data sent to the server
            params: additional parameters for the HTTP request
            response: response of the server
        """
        if response.status_code == 200:
            _return = response.json()
        else:
            _return = {"status": response.status_code, "message": response.text}
        dumpobj = {
            "DSP server": self.server,
            "url": url,
            "method": method,
            "headers": headers,
            "params": params,
            "body": json.loads(jsondata) if jsondata else None,
            "return-headers": dict(response.headers),
            "return": _return,
        }
        route_for_filename = url.replace(self.server, "").replace("/", "_")
        filename = f"{datetime.now().strftime('%Y-%m-%d %H.%M.%S.%f')} {method} {route_for_filename}.json"
        with open(self.dump_directory / filename, "w", encoding="utf-8") as f:
            json.dump(dumpobj, f, indent=4)

    def post(
        self,
        route: str,
        jsondata: Optional[str] = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']

        Returns:
            response from server
        """
        # timeout must be high enough,
        # otherwise the client can get a timeout error while the API is still processing the request
        # in that case, the client's retry will have undesired side effects (e.g. duplicated resources),
        # and the response of the original API call will be lost
        timeout = 60
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        headers = {}
        if jsondata:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.post(
            url=url,
            headers=headers,
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data=jsondata.encode("utf-8") if jsondata else None,
            timeout=timeout,
        )
        if self.dump:
            self._write_request_to_file(
                method="POST",
                url=url,
                headers=headers,
                jsondata=jsondata,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

    def get(
        self,
        route: str,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            headers: headers for the HTTP request

        Returns:
            response from server
        """
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        if not headers:
            headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(
            url=url,
            headers=headers,
            timeout=20,
        )
        if self.dump:
            self._write_request_to_file(
                method="GET",
                url=url,
                headers=headers,
                jsondata=None,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

    def put(
        self,
        route: str,
        jsondata: Optional[str] = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']

        Returns:
            response from server
        """
        # timeout must be high enough,
        # otherwise the client can get a timeout error while the API is still processing the request
        # in that case, the client's retry will fail, and the response of the original API call will be lost
        timeout = 60
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        headers = {}
        if jsondata:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.put(
            url=url,
            headers=headers,
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data=jsondata.encode("utf-8") if jsondata else None,
            timeout=timeout,
        )
        if self.dump:
            self._write_request_to_file(
                method="PUT",
                url=url,
                headers=headers,
                jsondata=jsondata,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

    def delete(
        self,
        route: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            params: additional parameters for the HTTP request

        Returns:
            response from server
        """
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.delete(
            url=url,
            headers=headers,
            params=params,
            timeout=20,
        )
        if self.dump:
            self._write_request_to_file(
                method="DELETE",
                url=url,
                headers=headers,
                jsondata=None,
                params=params,
                response=response,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())
