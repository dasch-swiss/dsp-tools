import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from typing import Any, Callable, Optional, cast

import regex
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
        token: session token received by the server after login
    """

    server: str
    token: Optional[str] = None
    # downtimes of server-side services -> API still processes request
    # -> retry too early has side effects (e.g. duplicated resources)
    timeout_put_post: int = field(init=False, default=30 * 60)
    timeout_get_delete: int = field(init=False, default=20)

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

    def _log_request(
        self,
        method: str,
        url: str,
        jsondata: Optional[str],
        params: Optional[dict[str, Any]],
        response: requests.Response,
        timeout: int,
        headers: dict[str, str] | None = None,
        uploaded_file: str | None = None,
    ) -> None:
        if response.status_code == 200:
            _return = response.json()
        else:
            _return = {"status": response.status_code, "message": response.text}
        if headers and "Authorization" in headers:
            headers["Authorization"] = regex.sub(r"Bearer .+", "Bearer <token>", headers["Authorization"])
        dumpobj = {
            "HTTP request": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timetout": timeout,
            "body": jsondata,
            "uploaded file": uploaded_file,
            "return-headers": dict(response.headers),
            "return": _return,
        }
        logger.debug(json.dumps(dumpobj))

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
        timeout = timeout or self.timeout_put_post

        request = partial(requests.post, url=url, headers=headers, timeout=timeout)
        if jsondata:
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data = jsondata.encode("utf-8") if jsondata else None
            request = partial(request, data=data)
        elif files:
            request = partial(request, files=files)

        response: Response = _try_network_action(request)
        self._log_request(
            method="POST",
            url=url,
            jsondata=jsondata,
            uploaded_file=files["file"][0] if files else None,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
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
        timeout = self.timeout_get_delete

        response: Response = _try_network_action(
            lambda: requests.get(
                url=url,
                headers=headers,
                timeout=timeout,
            )
        )
        self._log_request(
            method="GET",
            url=url,
            jsondata=None,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
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
        timeout = self.timeout_put_post

        response: Response = _try_network_action(
            lambda: requests.put(
                url=url,
                headers=headers,
                # if data is not encoded as bytes, issues can occur with non-ASCII characters,
                # where the content-length of the request will turn out to be different from the actual length
                data=jsondata.encode("utf-8") if jsondata else None,
                timeout=timeout,
            )
        )
        self._log_request(
            method="PUT",
            url=url,
            jsondata=jsondata,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
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
        timeout = self.timeout_get_delete

        response = requests.delete(
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
        self._log_request(
            method="DELETE",
            url=url,
            jsondata=None,
            params=params,
            response=response,
            headers=headers,
            timeout=timeout,
        )
        check_for_api_error(response)
        return cast(dict[str, Any], response.json())
