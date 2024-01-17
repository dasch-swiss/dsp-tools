import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from importlib.metadata import version
from typing import Any, Callable, Optional, cast

from requests import ReadTimeout, RequestException, Response, Session
from urllib3.exceptions import ReadTimeoutError

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.set_encoder import SetEncoder

HTTP_OK = 200
HTTP_SERVER_ERROR_LOWER = 500
HTTP_SERVER_ERROR_UPPER = 599

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
    session: Session = field(init=False, default=Session())
    # downtimes of server-side services -> API still processes request
    # -> retry too early has side effects (e.g. duplicated resources)
    timeout_put_post: int = field(init=False, default=30 * 60)
    timeout_get_delete: int = field(init=False, default=20)

    def __post_init__(self) -> None:
        self.session.headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'

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
        self.session.headers["Authorization"] = f"Bearer {self.token}"

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
        if data:
            headers = headers or {}
            headers["Content-Type"] = "application/json; charset=UTF-8"
        timeout = timeout or self.timeout_put_post

        request = partial(self.session.post, url=url, headers=headers, timeout=timeout)
        if data:
            # if data is not encoded as bytes, issues can occur with non-ASCII characters,
            # where the content-length of the request will turn out to be different from the actual length
            data_str = json.dumps(data, cls=SetEncoder, ensure_ascii=False).encode("utf-8")
            request = partial(request, data=data_str)
        elif files:
            request = partial(request, files=files)

        response = self._try_network_action(request)
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
        timeout = self.timeout_get_delete

        response = self._try_network_action(
            lambda: self.session.get(
                url=url,
                headers=headers,
                timeout=timeout,
            )
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
        if data:
            headers = headers or {}
            headers["Content-Type"] = f"{content_type}; charset=UTF-8"
        timeout = self.timeout_put_post

        response = self._try_network_action(
            lambda: self.session.put(
                url=url,
                headers=headers,
                # if data is not encoded as bytes, issues can occur with non-ASCII characters,
                # where the content-length of the request will turn out to be different from the actual length
                data=json.dumps(data, cls=SetEncoder, ensure_ascii=False).encode("utf-8") if data else None,
                timeout=timeout,
            )
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
        timeout = self.timeout_get_delete

        response = self.session.delete(
            url=url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
        return cast(dict[str, Any], response.json())

    def _should_retry(self, response: Response) -> bool:
        in_500_range = HTTP_SERVER_ERROR_LOWER <= response.status_code <= HTTP_SERVER_ERROR_UPPER
        try_again_later = "try again later" in response.text
        return try_again_later or in_500_range

    def _log_and_sleep(self, reason: str, retry_counter: int) -> None:
        msg = f"{reason}: Try reconnecting to DSP server, next attempt in {2 ** retry_counter} seconds..."
        print(f"{datetime.now()}: {msg}")
        logger.exception(f"{msg} ({retry_counter=:})")
        time.sleep(2**retry_counter)

    def _try_network_action(self, action: Callable[[], Response]) -> Response:
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
                response = action()
            except (TimeoutError, ReadTimeout, ReadTimeoutError):
                self._log_and_sleep(reason="Timeout Error", retry_counter=i)
                continue
            except (ConnectionError, RequestException):
                self.session.close()
                self.session = Session()
                self._log_and_sleep(reason="Network Error", retry_counter=i)
                continue

            if self._should_retry(response):
                self._log_and_sleep(reason="Transient Error", retry_counter=i)
                continue
            elif response.status_code != HTTP_OK:
                raise BaseError(
                    message="Permanently unable to execute the network action. See logs for more details.",
                    status_code=response.status_code,
                    json_content_of_api_response=response.text,
                    reason_from_api=response.reason,
                    api_route=response.url,
                )
            else:
                return response

        # after 7 vain attempts to create a response, try it a last time and let it escalate
        return action()
