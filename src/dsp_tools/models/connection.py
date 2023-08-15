from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Optional, cast

import requests

from dsp_tools.models.exceptions import BaseError


def check_for_api_error(response: requests.Response) -> None:
    """
    Check the response of an API request if it contains an error raised by DSP-API.

    Args:
        res: The requests.Response object that is returned by the API request

    Raises:
        BaseError: If the status code of the response is not 200
    """
    if response.status_code != 200:
        raise BaseError(
            message="KNORA-ERROR: status code=" + str(response.status_code) + "\nMessage:" + response.text,
            status_code=response.status_code,
            json_content_of_api_response=response.text,
            reason_from_api=response.reason,
            api_route=response.url,
        )


@dataclass
class Connection:
    """
    A Connection instance represents a connection to a DSP server.

    Attributes:
        server: address of the server, e.g https://api.dasch.swiss
        token: session token received by the server after login
        dump: if True, every request is written into a file
        dump_directory: directory where the HTTP requests are written
    """

    server: str
    user_email: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    dump: bool = False
    dump_directory: Path = Path("HTTP requests")

    def __post_init__(self) -> None:
        """
        Create dumping directory (if applicable),
        and login (if credentials are provided).

        Raises:
            BaseError: if DSP-API returns no token with the provided user credentials
        """
        if self.dump:
            self.dump_directory.mkdir(exist_ok=True)

        if self.user_email and self.password:
            response = self.post(
                path=self.server + "/v2/authentication",
                jsondata=json.dumps({"email": self.user_email, "password": self.password}),
            )
            if not response.get("token"):
                raise BaseError(
                    f"Error when trying to login with user '{self.user_email}' and password '{self.password} "
                    f"on server '{self.server}'",
                    json_content_of_api_response=json.dumps(response),
                    api_route="/v2/authentication",
                )
            self.token = response["token"]

    def write_request_to_file(
        self,
        method: str,
        route: str,
        headers: dict[str, str],
        jsondata: Optional[str],
        params: Optional[dict[str, Any]],
        response: requests.Response,
    ) -> None:
        """
        Write the request and response to a file.

        Args:
            method: HTTP method (POST, GET, PUT, DELETE)
            route: route of DSP-API that was called
            headers: headers of the HTTP request
            jsondata: data sent to the server
            response: response of the server
        """
        if response.status_code == 200:
            _return = response.json()
        else:
            _return = {"status": response.status_code, "message": response.text}
        dumpobj = {
            "DSP server": self.server,
            "route": route,
            "method": method,
            "headers": headers,
            "params": params,
            "body": json.loads(jsondata) if jsondata else None,
            "return-headers": dict(response.headers),
            "return": _return,
        }
        filename = f"{datetime.now().strftime('%Y-%m-%d %H.%M.%S.%f')} {method} {route.replace('/', '_')}.json"
        with open(self.dump_directory / filename, "w", encoding="utf-8") as f:
            json.dump(dumpobj, f, indent=4)

    def post(
        self,
        path: str,
        jsondata: Optional[str] = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            path: Path of RESTful route
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']

        Returns:
            response from server
        """
        # timeout must be None,
        # otherwise the client can get a timeout error while the API is still processing the request
        # in that case, the client's retry will fail, and the response of the original API call is lost
        timeout = None
        if not path.startswith("/"):
            path = "/" + path
        headers = {}
        if jsondata:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.post(
            self.server + path,
            headers=headers,
            data=jsondata,
            timeout=timeout,
        )
        if self.dump:
            self.write_request_to_file(
                method="POST",
                route=path,
                headers=headers,
                jsondata=jsondata,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def get(
        self,
        path: str,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            path: Path of RESTful route
            headers: headers for the HTTP request

        Returns:
            response from server
        """
        if not path.startswith("/"):
            path = "/" + path
        if not headers:
            headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.get(url=self.server + path, headers=headers, timeout=20)
        if self.dump:
            self.write_request_to_file(
                method="GET",
                route=path,
                headers=headers,
                jsondata=None,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def put(
        self,
        path: str,
        jsondata: Optional[str] = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            path: Path of RESTful route
            jsondata: Valid JSON as string
            content_type: HTTP Content-Type [default: 'application/json']
        """
        # timeout must be None,
        # otherwise the client can get a timeout error while the API is still processing the request
        # in that case, the client's retry will fail, and the response of the original API call is lost
        timeout = None
        if not path.startswith("/"):
            path = "/" + path
        headers = {}
        if jsondata:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = requests.put(
            self.server + path,
            headers=headers,
            data=jsondata,
            timeout=timeout,
        )
        if self.dump:
            self.write_request_to_file(
                method="PUT",
                route=path,
                headers=headers,
                jsondata=jsondata,
                params=None,
                response=response,
            )
        check_for_api_error(response)
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def delete(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            path: Path of RESTful route
            params: additional parameters for the HTTP request

        Returns:
            response from server
        """
        if not path.startswith("/"):
            path = "/" + path
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = requests.delete(
            self.server + path,
            headers=headers,
            params=params,
            timeout=20,
        )
        if self.dump:
            self.write_request_to_file(
                method="DELETE",
                route=path,
                headers=headers,
                jsondata=None,
                params=params,
                response=response,
            )
        check_for_api_error(response)
        json_response = cast(dict[str, Any], response.json())
        return json_response
