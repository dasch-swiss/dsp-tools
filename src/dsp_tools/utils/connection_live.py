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
from typing import Optional
from typing import cast

import regex
from requests import ReadTimeout
from requests import RequestException
from requests import Response
from requests import Session

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_log_filename_str
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.set_encoder import SetEncoder

HTTP_OK = 200
HTTP_UNAUTHORIZED = 401

logger = get_logger(__name__)
LOGFILES = get_log_filename_str(logger)


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
        if self.server.endswith("/"):
            self.server = self.server[:-1]

    def login(self, email: str, password: str) -> None:
        """
        Retrieve a session token and store it as class attribute.

        Args:
            email: email address of the user
            password: password of the user

        Raises:
            UserError: if DSP-API returns no token with the provided user credentials
        """
        try:
            response = self.post(
                route="/v2/authentication",
                data={"email": email, "password": password},
                timeout=10,
            )
        except BadCredentialsError:
            raise UserError(f"Username and/or password are not valid on server '{self.server}'") from None
        except PermanentConnectionError as e:
            raise UserError(e.message) from None
        if not response.get("token"):
            raise UserError("Unable to retrieve a token from the server with the provided credentials.")
        self.token = response["token"]
        self.session.headers["Authorization"] = f"Bearer {self.token}"

    def logout(self) -> None:
        """
        Delete the token on the server and in this class.
        """
        if self.token:
            self.delete(route="/v2/authentication")
            self.token = None
            del self.session.headers["Authorization"]

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
            PermanentConnectionError: if the server returns a permanent error
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
            PermanentConnectionError: if the server returns a permanent error
        """
        params = RequestParameters("GET", self._make_url(route), self.timeout_get_delete, headers=headers)
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
            PermanentConnectionError: if the server returns a permanent error
        """
        if data:
            headers = headers or {}
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json; charset=UTF-8"
        params = RequestParameters("PUT", self._make_url(route), self.timeout_put_post, data, headers)
        response = self._try_network_action(params)
        return cast(dict[str, Any], response.json())

    def delete(
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
            PermanentConnectionError: if the server returns a permanent error
        """
        params = RequestParameters("DELETE", self._make_url(route), self.timeout_get_delete, headers=headers)
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
            PermanentConnectionError: if the server returns a permanent error
            unexpected exceptions: if the action fails with an unexpected exception

        Returns:
            the return value of action
        """
        action = partial(self.session.request, **params.as_kwargs())
        for i in range(7):
            try:
                self._log_request(params)
                response = action()
            except (TimeoutError, ReadTimeout):
                self._log_and_sleep(reason="Timeout Error", retry_counter=i, exc_info=True)
                continue
            except (ConnectionError, RequestException):
                self._renew_session()
                self._log_and_sleep(reason="Connection Error raised", retry_counter=i, exc_info=True)
                continue

            self._log_response(response)
            if response.status_code == HTTP_OK:
                return response

            self._handle_non_ok_responses(response, params.url, i)

        # after 7 vain attempts to create a response, try it a last time and let it escalate
        return action()

    def _handle_non_ok_responses(self, response: Response, request_url: str, retry_counter: int) -> None:
        if "v2/authentication" in request_url and response.status_code == HTTP_UNAUTHORIZED:
            raise BadCredentialsError("Bad credentials")
        in_500_range = 500 <= response.status_code < 600
        try_again_later = "try again later" in response.text.lower()
        should_retry = (try_again_later or in_500_range) and not self._in_testing_environment()
        if should_retry:
            self._log_and_sleep("Transient Error", retry_counter, exc_info=False)
            return None
        else:
            msg = f"Permanently unable to execute the network action. See logs for more details: {LOGFILES}"
            raise PermanentConnectionError(msg)

    def _renew_session(self) -> None:
        self.session.close()
        self.session = Session()
        self.session.headers["User-Agent"] = f'DSP-TOOLS/{version("dsp-tools")}'
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

    def _log_and_sleep(self, reason: str, retry_counter: int, exc_info: bool) -> None:
        msg = f"{reason}: Try reconnecting to DSP server, next attempt in {2 ** retry_counter} seconds..."
        print(f"{datetime.now()}: {msg}")
        logger.error(f"{msg} ({retry_counter=:})", exc_info=exc_info)
        time.sleep(2**retry_counter)

    def _log_response(self, response: Response) -> None:
        dumpobj: dict[str, Any] = {
            "status_code": response.status_code,
            "headers": self._anonymize(dict(response.headers)),
        }
        try:
            dumpobj["content"] = self._anonymize(json.loads(response.text))
        except json.JSONDecodeError:
            dumpobj["content"] = response.text if "token" not in response.text else "***"
        logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")

    def _anonymize(self, data: dict[str, Any] | None) -> dict[str, Any] | None:
        if not data:
            return data
        data = data.copy()
        if "token" in data:
            data["token"] = self._mask(data["token"])
        if "Set-Cookie" in data:
            data["Set-Cookie"] = self._mask(data["Set-Cookie"])
        if "Authorization" in data:
            if match := regex.search(r"^Bearer (.+)", data["Authorization"]):
                data["Authorization"] = f"Bearer {self._mask(match.group(1))}"
        if "password" in data:
            data["password"] = "*" * len(data["password"])
        return data

    def _mask(self, sensitive_info: str) -> str:
        unmasked_until = 5
        if len(sensitive_info) <= unmasked_until * 2:
            return "*" * len(sensitive_info)
        else:
            return f"{sensitive_info[:unmasked_until]}[+{len(sensitive_info) - unmasked_until}]"

    def _in_testing_environment(self) -> bool:
        in_testing_env = os.getenv("DSP_TOOLS_TESTING")  # set in .github/workflows/tests-on-push.yml
        return in_testing_env == "true"

    def _log_request(self, params: RequestParameters) -> None:
        dumpobj = {
            "method": params.method,
            "url": params.url,
            "headers": self._anonymize(dict(self.session.headers) | (params.headers or {})),
            "timeout": params.timeout,
        }
        if params.data:
            dumpobj["data"] = self._anonymize(params.data)
        if params.files:
            dumpobj["files"] = params.files["file"][0]
        logger.debug(f"REQUEST: {json.dumps(dumpobj, cls=SetEncoder)}")
