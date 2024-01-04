import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable, Optional, cast

import requests
from requests import ReadTimeout, RequestException, Response
from urllib3.exceptions import ReadTimeoutError

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def _try_network_action(
    action: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Helper method that tries 7 times to execute an action.
    If a timeout error, a ConnectionError, a requests.exceptions.RequestException, or a non-permanent BaseError occors,
    it waits and retries.
    The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.
    If another exception occurs, it escalates.

    Args:
        action: a lambda with the code to be executed, or a function
        args: positional arguments for the action
        kwargs: keyword arguments for the action

    Raises:
        BaseError: if the action fails permanently
        unexpected exceptions: if the action fails with an unexpected exception

    Returns:
        the return value of action
    """
    action_as_str = f"{action=}, {args=}, {kwargs=}"
    for i in range(7):
        try:
            if args and not kwargs:
                return action(*args)
            elif not args and kwargs:
                return action(**kwargs)
            elif args and kwargs:
                return action(*args, **kwargs)
            else:
                return action()
        except (TimeoutError, ReadTimeout, ReadTimeoutError):
            msg = f"Timeout Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
            print(f"{datetime.now()}: {msg}")
            logger.error(f"{msg} {action_as_str} (retry-counter {i=:})", exc_info=True)
            time.sleep(2**i)
        except (ConnectionError, RequestException):
            msg = f"Network Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
            print(f"{datetime.now()}: {msg}")
            logger.error(f"{msg} {action_as_str} (retry-counter {i=:})", exc_info=True)
            time.sleep(2**i)
        except BaseError as err:
            in_500_range = False
            if err.status_code:
                in_500_range = 500 <= err.status_code < 600
            try_again_later = "try again later" in err.message
            if try_again_later or in_500_range:
                msg = f"Transient Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
                print(f"{datetime.now()}: {msg}")
                logger.error(f"{msg} {action_as_str} (retry-counter {i=:})", exc_info=True)
                time.sleep(2**i)
            else:
                raise err

    logger.error("Permanently unable to execute the network action. See logs for more details.")
    raise BaseError("Permanently unable to execute the network action. See logs for more details.")


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
        token: session token received by the server after login
    """

    server: str
    dump: bool = False
    dump_directory: Path = field(init=False, default=Path("HTTP requests"))
    token: Optional[str] = None
    # downtimes of server-side services -> API still processes request
    # -> retry too early has side effects (e.g. duplicated resources)
    timeout_put_post: int = field(init=False, default=30 * 60)
    timeout_get_delete: int = field(init=False, default=20)

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
        jsondata: Optional[str],
        params: Optional[dict[str, Any]],
        response: requests.Response,
        headers: dict[str, str] | None = None,
        uploaded_file: Optional[str] = None,
    ) -> None:
        """
        Write the request and response to a file.

        Args:
            method: HTTP method (POST, GET, PUT, DELETE)
            url: complete URL (server + route of DSP-API) that was called
            jsondata: data sent to the server
            params: additional parameters for the HTTP request
            response: response of the server
            headers: headers of the HTTP request
            uploaded_file: path to the file that was uploaded, if any
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
            "uploaded file": uploaded_file,
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
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            files: files to be uploaded, if any
            headers: headers for the HTTP request
            timeout: timeout of the HTTP request, or None if the default should be used

        Returns:
            response from server
        """
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        if not headers:
            headers = {}
        if jsondata:
            headers["Content-Type"] = "application/json; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = partial(requests.post, url=url, headers=headers, timeout=timeout or self.timeout_put_post)
        if jsondata:
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data = jsondata.encode("utf-8") if jsondata else None
            request = partial(request, data=data)
        elif files:
            request = partial(request, files=files)

        response: Response = _try_network_action(request)
        if self.dump:
            self._write_request_to_file(
                method="POST",
                url=url,
                jsondata=jsondata,
                uploaded_file=files["file"][0] if files else None,
                params=None,
                response=response,
                headers=headers,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

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

        response: Response = _try_network_action(
            lambda: requests.get(
                url=url,
                headers=headers,
                timeout=self.timeout_get_delete,
            )
        )
        if self.dump:
            self._write_request_to_file(
                method="GET",
                url=url,
                jsondata=None,
                params=None,
                response=response,
                headers=headers,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

    def put(
        self,
        route: str,
        jsondata: Optional[str] = None,
        headers: dict[str, str] | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            jsondata: Valid JSON as string
            headers: headers of the HTTP request
            content_type: HTTP Content-Type [default: 'application/json']

        Returns:
            response from server
        """
        if not route.startswith("/"):
            route = f"/{route}"
        url = self.server + route
        if not headers:
            headers = {}
        if jsondata:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response: Response = _try_network_action(
            lambda: requests.put(
                url=url,
                headers=headers,
                # if data is not encoded as bytes, issues can occur with non-ASCII characters,
                # where the content-length of the request will turn out to be different from the actual length
                data=jsondata.encode("utf-8") if jsondata else None,
                timeout=self.timeout_put_post,
            )
        )
        if self.dump:
            self._write_request_to_file(
                method="PUT",
                url=url,
                jsondata=jsondata,
                params=None,
                response=response,
                headers=headers,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())

    def delete(
        self,
        route: str,
        params: Optional[dict[str, Any]] = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            params: additional parameters for the HTTP request
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
        response = requests.delete(
            url=url,
            headers=headers,
            params=params,
            timeout=self.timeout_get_delete,
        )
        if self.dump:
            self._write_request_to_file(
                method="DELETE",
                url=url,
                jsondata=None,
                params=params,
                response=response,
                headers=headers,
            )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())
