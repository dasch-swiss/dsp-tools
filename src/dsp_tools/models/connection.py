from datetime import datetime
import json
from typing import Any, Optional, Union, cast

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


class Connection:
    """
    An Connection instance represents a connection to a DSP server.

    Attributes:
        server: dddress of the server, e.g https://api.dasch.swiss
        prefixes: ontology prefixes used
        token: session token received by the server after login
        log: if True, the requests are written into a file
    """

    server: str
    prefixes: Optional[dict[str, str]] = None
    token: Union[str, None] = None
    log: bool = False

    def login(self, email: str, password: str) -> None:
        """
        Retrieve a session token.

        Args:
            email: Email of user
            password: Password of the user
        """
        response = requests.post(
            self.server + "/v2/authentication",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            data=json.dumps({"email": email, "password": password}),
            timeout=20,
        )
        check_for_api_error(response)
        result = response.json()
        self.token = result["token"]

    def start_logging(self) -> None:
        """Start writing every API call to a file"""
        self.log = True

    def stop_logging(self) -> None:
        """Stop writing every API call to a file"""
        self.log = False

    def logout(self) -> None:
        """Delete the session token"""
        if self.token:
            response = requests.delete(
                self.server + "/v2/authentication",
                headers={"Authorization": "Bearer " + self.token},
                timeout=20,
            )
            check_for_api_error(response)
            self.token = None

    def write_log_file(
        self,
        method: str,
        route: str,
        headers: dict[str, str],
        jsondata: Optional[str],
        params: Optional[dict[str, Any]],
        response: requests.Response,
    ) -> None:
        """
        If logging is enabled (self.log == True), write the request and response to a file.

        Args:
            method: HTTP method (POST, GET, PUT, DELETE)
            route: route of DSP-API that was called
            headers: headers of the HTTP request
            jsondata: data sent to the server
            response: response of the server
        """
        if not self.log:
            return
        logobj = {
            "DSP server": self.server,
            "method": method,
            "headers": headers,
            "route": route,
            "params": params,
            "body": json.loads(jsondata) if jsondata else None,
            "return-headers": dict(response.headers),
            "return": response.json()
            if response.status_code == 200
            else {"status": str(response.status_code), "message": response.text},
        }
        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} POST {route.replace('/', '_')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(logobj, f, indent=4)

    def post(
        self,
        path: str,
        jsondata: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            path: Path of RESTful route
            jsondata: Valid JSON as string

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
            headers = {"Content-Type": "application/json; charset=UTF-8"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token

        response = requests.post(
            self.server + path,
            headers=headers,
            data=jsondata,
            timeout=timeout,
        )
        self.write_log_file(
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
            headers["Authorization"] = "Bearer " + self.token

        response = requests.get(url=self.server + path, headers=headers, timeout=20)
        self.write_log_file(
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
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        if jsondata:
            headers["Content-Type"] = content_type + "; charset=UTF-8"

        response = requests.put(
            self.server + path,
            headers=headers,
            data=jsondata,
            timeout=timeout,
        )
        self.write_log_file(
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
            headers = {"Authorization": "Bearer " + self.token}
        response = requests.delete(
            self.server + path,
            headers=headers,
            params=params,
            timeout=20,
        )
        self.write_log_file(
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
