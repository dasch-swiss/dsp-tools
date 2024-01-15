import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from importlib.metadata import version
from typing import Any, Callable, Optional, cast

import regex
import requests
from requests import ReadTimeout, RequestException, Response
from urllib3.exceptions import ReadTimeoutError

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.set_encoder import SetEncoder

logger = get_logger(__name__)


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
            data={"email": email, "password": password},
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
        data: dict[str, Any] | None,
        params: Optional[dict[str, Any]],
        response: requests.Response,
        timeout: int,
        headers: dict[str, str] | None = None,
        uploaded_file: str | None = None,
    ) -> None:
        if response.status_code == 200:
            _return = response.json()
            if "token" in _return:
                _return["token"] = "<token>"
        else:
            _return = {"status": response.status_code, "message": response.text}
        if headers and "Authorization" in headers:
            headers["Authorization"] = regex.sub(r"Bearer .+", "Bearer <token>", headers["Authorization"])
        if data and "password" in data:
            data["password"] = "<password>"
        return_headers = dict(response.headers)
        if "Set-Cookie" in return_headers:
            return_headers["Set-Cookie"] = "<cookie>"
        dumpobj = {
            "HTTP request": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timetout": timeout,
            "payload": data,
            "uploaded file": uploaded_file,
            "return-headers": return_headers,
            "return": _return,
        }
        logger.debug(json.dumps(dumpobj, cls=SetEncoder))

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Make a HTTP POST request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            data: payload of the HTTP request
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
        headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if data:
            headers["Content-Type"] = "application/json; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        timeout = timeout or self.timeout_put_post

        request = partial(requests.post, url=url, headers=headers, timeout=timeout)
        if data:
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data_str = json.dumps(data, cls=SetEncoder, ensure_ascii=False).encode("utf-8")
            request = partial(request, data=data_str)
        elif files:
            request = partial(request, files=files)

        response: Response = self._try_network_action(request)
        self._log_request(
            method="POST",
            url=url,
            data=data,
            uploaded_file=files["file"][0] if files else None,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
        )
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
        headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        timeout = self.timeout_get_delete

        response: Response = self._try_network_action(
            lambda: requests.get(
                url=url,
                headers=headers,
                timeout=timeout,
            )
        )
        self._log_request(
            method="GET",
            url=url,
            data=None,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
        )
        return cast(dict[str, Any], response.json())

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        content_type: str = "application/json",
    ) -> dict[str, Any]:
        """
        Make a HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            data: payload of the HTTP request
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
        headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if data:
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        timeout = self.timeout_put_post

        response: Response = self._try_network_action(
            lambda: requests.put(
                url=url,
                headers=headers,
                # if data is not encoded as bytes, issues can occur with non-ASCII characters,
                # where the content-length of the request will turn out to be different from the actual length
                data=json.dumps(data, cls=SetEncoder, ensure_ascii=False).encode("utf-8") if data else None,
                timeout=timeout,
            )
        )
        self._log_request(
            method="PUT",
            url=url,
            data=data,
            params=None,
            response=response,
            headers=headers,
            timeout=timeout,
        )
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
        headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
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
            data=None,
            params=params,
            response=response,
            headers=headers,
            timeout=timeout,
        )
        return cast(dict[str, Any], response.json())

    def _try_network_action(self, action: Callable[..., Any]) -> Any:
        """
        Try 7 times to execute a HTTP request.
        If a timeout error, a ConnectionError, or a requests.RequestException occur,
        or if the response indicates that there is a non-permanent server-side problem,
        this function waits and retries the HTTP request.
        The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.

        Args:
            action: a lambda with the code to be executed, or a function

        Raises:
            BaseError: if the action fails permanently
            unexpected exceptions: if the action fails with an unexpected exception

        Returns:
            the return value of action
        """
        for i in range(7):
            try:
                response: requests.Response = action()
            except (TimeoutError, ReadTimeout, ReadTimeoutError):
                msg = f"Timeout Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
                print(f"{datetime.now()}: {msg}")
                logger.error(f"{msg} (retry-counter {i=:})", exc_info=True)
                time.sleep(2**i)
                continue
            except (ConnectionError, RequestException):
                msg = f"Network Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
                print(f"{datetime.now()}: {msg}")
                logger.error(f"{msg} (retry-counter {i=:})", exc_info=True)
                time.sleep(2**i)
                continue

            in_500_range = 500 <= response.status_code < 600
            try_again_later = "try again later" in response.text
            if try_again_later or in_500_range:
                msg = f"Transient Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
                print(f"{datetime.now()}: {msg}")
                logger.error(f"{msg} (retry-counter {i=:})", exc_info=True)
                time.sleep(2**i)
                continue
            elif response.status_code != 200:
                raise BaseError(
                    message="Permanently unable to execute the network action. See logs for more details.",
                    status_code=response.status_code,
                    json_content_of_api_response=response.text,
                    reason_from_api=response.reason,
                    api_route=response.url,
                )
            else:
                return response
