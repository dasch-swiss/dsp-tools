import json
import os
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from functools import partial
from importlib.metadata import version
from typing import Any
from typing import Literal
from typing import Never
from typing import cast

import regex
from loguru import logger
from requests import JSONDecodeError
from requests import ReadTimeout
from requests import RequestException
from requests import Response
from requests import Session

from dsp_tools.models.exceptions import InvalidInputError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.utils.authentication_client import AuthenticationClient
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH
from dsp_tools.utils.set_encoder import SetEncoder

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401


@dataclass
class RequestParameters:
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    timeout: int
    data: dict[str, Any] | None = None
    data_serialized: bytes | None = field(init=False, default=None)
    headers: dict[str, str] | None = None
    files: dict[str, tuple[str, Any]] | None = None

    def __post_init__(self) -> None:
        self.data_serialized = self._serialize_payload(self.data)

    def _serialize_payload(self, payload: dict[str, Any] | None) -> bytes | None:
        # If data is not encoded as bytes, issues can occur with non-ASCII characters,
        # where the content-length of the request will turn out to be different from the actual length.
        return json.dumps(payload, cls=SetEncoder, ensure_ascii=False).encode("utf-8") if payload else None

    def as_kwargs(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "timeout": self.timeout,
            "data": self.data_serialized,
            "headers": self.headers,
            "files": self.files,
        }


@dataclass
class ConnectionLive(Connection):
    """
    A Connection instance represents a connection to a DSP server.

    Attributes:
        server: address of the server, e.g https://api.dasch.swiss
        token: session token received by the server after login
    """

    server: str
    authenticationClient: AuthenticationClient | None = None
    session: Session = field(init=False, default=Session())
    # downtimes of server-side services -> API still processes request
    # -> retry too early has side effects (e.g. duplicated resources)
    timeout_put_post: int = field(init=False, default=30 * 60)
    timeout_get: int = field(init=False, default=20)

    def __post_init__(self) -> None:
        self.session.headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if self.server.endswith("/"):
            self.server = self.server[:-1]
        if self.authenticationClient and (token := self.authenticationClient.get_token()):
            self.session.headers["Authorization"] = f"Bearer {token}"

    def logout(self) -> None:
        """
        Remove the authorization header from the connection's session.
        """
        del self.session.headers["Authorization"]

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP POST request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            data: payload of the HTTP request
            files: files to be uploaded, if any
            headers: headers for the HTTP request
            timeout: timeout of the HTTP request, or None if the default should be used

        Returns:
            response from server

        Raises:
            PermanentConnectionError: if all attempts have failed
            InvalidInputError: if the API responds with a permanent error because of invalid input data
        """
        if data:
            headers = headers or {}
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json; charset=UTF-8"
        params = RequestParameters(
            "POST", self._make_url(route), timeout or self.timeout_put_post, data, headers, files
        )
        response = self._try_network_action(params)
        return cast(dict[str, Any], response.json())

    def get(
        self,
        route: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            headers: headers for the HTTP request

        Returns:
            response from server

        Raises:
            PermanentConnectionError: if all attempts have failed
            InvalidInputError: if the API responds with a permanent error because of invalid input data
        """
        params = RequestParameters("GET", self._make_url(route), self.timeout_get, headers=headers)
        response = self._try_network_action(params)
        return cast(dict[str, Any], response.json())

    def put(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP GET request to the server to which this connection has been established.

        Args:
            route: route that will be called on the server
            data: payload of the HTTP request
            headers: headers of the HTTP request

        Returns:
            response from server

        Raises:
            PermanentConnectionError: if all attempts have failed
            InvalidInputError: if the API responds with a permanent error because of invalid input data
        """
        if data:
            headers = headers or {}
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json; charset=UTF-8"
        params = RequestParameters("PUT", self._make_url(route), self.timeout_put_post, data, headers)
        response = self._try_network_action(params)
        return cast(dict[str, Any], response.json())

    def _make_url(self, route: str) -> str:
        if not route.startswith("/"):
            route = f"/{route}"
        return self.server + route

    def _try_network_action(self, params: RequestParameters) -> Response:
        """
        Try 7 times to execute an HTTP request.
        If a timeout error, a ConnectionError, or a requests.RequestException occur,
        or if the response indicates that there is a non-permanent server-side problem,
        this function waits and retries the HTTP request.
        The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.

        Args:
            params: keyword arguments for the HTTP request

        Raises:
            BadCredentialsError: if the server returns a 401 status code on the route /v2/authentication
            PermanentConnectionError: if all attempts have failed
            InvalidInputError: if the API responds with a permanent error because of invalid input data
            unexpected exceptions: if the action fails with an unexpected exception

        Returns:
            the return value of action
        """
        action = partial(self.session.request, **params.as_kwargs())
        for i in range(7):
            try:
                self._log_request(params)
                response = action()
            except (TimeoutError, ReadTimeout) as err:
                self._log_and_raise_timeouts(err)
            except (ConnectionError, RequestException):
                self._renew_session()
                self._log_and_sleep(reason="Connection Error raised", retry_counter=i, exc_info=True)
                continue

            self._log_response(response)
            if response.status_code == HTTP_OK:
                return response

            self._handle_non_ok_responses(response, i)

        # if all attempts have failed, raise error
        msg = f"Permanently unable to execute the network action. See {WARNINGS_SAVEPATH} for more information."
        raise PermanentConnectionError(msg)

    def _handle_non_ok_responses(self, response: Response, retry_counter: int) -> None:
        if _should_retry(response):
            self._log_and_sleep("Transient Error", retry_counter, exc_info=False)
            return None
        else:
            msg = "Permanently unable to execute the network action. "
            if original_str := regex.search(r'{"knora-api:error":"dsp\.errors\.(.*)","@context', str(response.content)):
                msg += f"\n{' '*37}Original Message: {original_str.group(1)}\n"
                if original_str.group(1).startswith("OntologyConstraintException"):
                    msg += f"See {WARNINGS_SAVEPATH} for more information."
                    raise InvalidInputError(msg)
            msg += f"See {WARNINGS_SAVEPATH} for more information."
            raise PermanentConnectionError(msg)

    def _renew_session(self) -> None:
        self.session.close()
        self.session = Session()
        self.session.headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if self.authenticationClient and (token := self.authenticationClient.get_token()):
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _log_and_sleep(self, reason: str, retry_counter: int, exc_info: bool) -> None:
        msg = f"{reason}: Try reconnecting to DSP server, next attempt in {2 ** retry_counter} seconds..."
        print(f"{datetime.now()}: {msg}")
        if exc_info:
            logger.opt(exception=True).error(f"{msg} ({retry_counter=:})")
        else:
            logger.error(f"{msg} ({retry_counter=:})")
        time.sleep(2**retry_counter)

    def _log_and_raise_timeouts(self, error: TimeoutError | ReadTimeout) -> Never:
        msg = f"A '{error.__class__.__name__}' occurred during the connection to the DSP server."
        print(f"{datetime.now()}: {msg}")
        logger.exception(msg)
        raise PermanentTimeOutError(msg) from None

    def _log_response(self, response: Response) -> None:
        dumpobj: dict[str, Any] = {
            "status_code": response.status_code,
            "headers": _sanitize_headers(dict(response.headers)),
        }
        try:
            dumpobj["content"] = response.json()
        except JSONDecodeError:
            dumpobj["content"] = response.text
        logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")

    def _log_request(self, params: RequestParameters) -> None:
        dumpobj = {
            "method": params.method,
            "url": params.url,
            "headers": _sanitize_headers(dict(self.session.headers) | (params.headers or {})),  # type: ignore[operator]
            "timeout": params.timeout,
        }
        if params.data:
            data = params.data.copy()
            if "password" in data:
                data["password"] = "***"
            dumpobj["data"] = data
        if params.files:
            dumpobj["files"] = params.files["file"][0]
        logger.debug(f"REQUEST: {json.dumps(dumpobj, cls=SetEncoder)}")


def _sanitize_headers(headers: dict[str, str | bytes]) -> dict[str, str]:
    def _mask(key: str, value: str | bytes) -> str:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if key == "Authorization" and value.startswith("Bearer "):
            return "Bearer ***"
        if key == "Set-Cookie":
            return "***"
        return value

    return {k: _mask(k, v) for k, v in headers.items()}


def _should_retry(response: Response) -> bool:
    in_500_range = 500 <= response.status_code < 600
    try_again_later = "try again later" in response.text.lower()
    in_testing_env = os.getenv("DSP_TOOLS_TESTING") == "true"  # set in .github/workflows/tests-on-push.yml
    return (try_again_later or in_500_range) and not in_testing_env
