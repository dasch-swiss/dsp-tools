from dataclasses import dataclass
from dataclasses import field
from functools import partial
from importlib.metadata import version
from typing import Any
from typing import Literal
from typing import cast

import regex
from requests import ReadTimeout
from requests import RequestException
from requests import Response
from requests import Session

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.connection import Connection
from dsp_tools.config.logger_config import WARNINGS_SAVEPATH
from dsp_tools.error.exceptions import InvalidInputError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.utils.request_utils import PostFiles
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_and_raise_timeouts
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_request_failure_and_sleep
from dsp_tools.utils.request_utils import log_response
from dsp_tools.utils.request_utils import should_retry

HTTP_OK = 200


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
        self.session.headers["User-Agent"] = f"DSP-TOOLS/{version('dsp-tools')}"
        if self.server.endswith("/"):
            self.server = self.server[:-1]
        if self.authenticationClient and (token := self.authenticationClient.get_token()):
            self.session.headers["Authorization"] = f"Bearer {token}"

    def post(
        self,
        route: str,
        data: dict[str, Any] | None = None,
        files: PostFiles | None = None,
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
        Try several times to execute an HTTP request.
        If a timeout error, a ConnectionError, or a requests.RequestException occur,
        or if the response indicates that there is a non-permanent server-side problem,
        this function waits and retries the HTTP request.

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
        num_of_retries = 24  # xmlupload must handle > 45 min fuseki downtime due to compaction, see DEV-5089
        for retry_counter in range(num_of_retries):
            try:
                log_request(params, dict(self.session.headers))
                response = action()
            except (TimeoutError, ReadTimeout) as err:
                log_and_raise_timeouts(err)
            except (ConnectionError, RequestException):
                self._renew_session()
                log_request_failure_and_sleep(
                    reason="Connection Error raised", retry_counter=retry_counter, exc_info=True
                )
                continue

            log_response(response)
            if response.status_code == HTTP_OK:
                return response

            self._handle_non_ok_responses(response, retry_counter)

        # if all attempts have failed, raise error
        msg = f"Permanently unable to execute the network action. See {WARNINGS_SAVEPATH} for more information."
        raise PermanentConnectionError(msg)

    def _handle_non_ok_responses(self, response: Response, retry_counter: int) -> None:
        if should_retry(response):
            log_request_failure_and_sleep("Transient Error", retry_counter, exc_info=False)
            return None
        api_msg = self._extract_original_api_err_msg(str(response.content))
        blame = self._determine_blame(api_msg)
        if blame == "client":
            raise InvalidInputError(api_msg)
        else:
            msg = f"Permanently unable to execute the network action.\n{' ' * 37}Original Message: {api_msg}\n"
            raise PermanentConnectionError(msg)

    def _extract_original_api_err_msg(self, response_content: str) -> str:
        if found := regex.search(r'{"knora-api:error":"dsp\.errors\.(.*)","@context', response_content):
            api_msg = found.group(1)
        if found := regex.search(r'{"message":"(.+)"}', response_content):
            api_msg = found.group(1)
        else:
            api_msg = str(response_content)
        return api_msg

    def _determine_blame(self, api_msg: str) -> Literal["server", "client"]:
        api_msg = api_msg.lower()
        client_markers = [
            "OntologyConstraintException",
            "NotFoundException",
            "One or more resources were not found",
            "does not allow more than one value for property",
            "Duplicate values for property",
            "Text value contains invalid characters",
        ]
        blame: Literal["server", "client"] = "server"
        if any(x.lower() in api_msg for x in client_markers):
            blame = "client"
        return blame

    def _renew_session(self) -> None:
        self.session.close()
        self.session = Session()
        self.session.headers["User-Agent"] = f"DSP-TOOLS/{version('dsp-tools')}"
        if self.authenticationClient and (token := self.authenticationClient.get_token()):
            self.session.headers["Authorization"] = f"Bearer {token}"
