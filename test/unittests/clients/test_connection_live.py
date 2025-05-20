# mypy: disable-error-code="method-assign"

import json
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from importlib.metadata import version
from typing import Any
from typing import Literal
from typing import cast
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import regex
from requests import ReadTimeout
from requests import RequestException

from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.utils.request_utils import PostFile
from dsp_tools.utils.request_utils import PostFiles
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request


@dataclass
class SessionMock:
    responses: tuple[Any, ...]
    headers: dict[str, Any] = field(default_factory=dict)
    counter = 0

    def request(self, **kwargs: Any) -> Any:  # noqa: ARG002
        response = self.responses[self.counter]
        self.counter += 1
        if isinstance(response, BaseException):
            raise response
        return response


def test_post() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.post(route="/v2/resources")
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "POST"
    assert expected_params.url == "http://example.com/v2/resources"
    assert expected_params.data is None
    assert expected_params.headers is None
    assert expected_params.files is None


def test_post_with_data() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.post(route="/v2/resources", data={"foo": "bar"})
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "POST"
    assert expected_params.url == "http://example.com/v2/resources"
    assert expected_params.data == {"foo": "bar"}
    assert expected_params.headers == {"Content-Type": "application/json; charset=UTF-8"}
    assert expected_params.files is None


def test_post_with_file() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    file = PostFiles([PostFile("path/to/file.jpg", b"some bytes")])
    con.post(route="/upload", files=file)
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "POST"
    assert expected_params.url == "http://example.com/upload"
    assert expected_params.data is None
    assert expected_params.headers is None
    assert expected_params.files == file


def test_get() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.get(route="/admin/groups")
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "GET"
    assert expected_params.url == "http://example.com/admin/groups"
    assert expected_params.data is None
    assert expected_params.headers is None
    assert expected_params.files is None


def test_put() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.put(route="/v2/values")
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "PUT"
    assert expected_params.url == "http://example.com/v2/values"
    assert expected_params.data is None
    assert expected_params.headers is None
    assert expected_params.files is None


def test_put_with_data() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.put(route="/v2/values", data={"foo": "bar"})
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "PUT"
    assert expected_params.url == "http://example.com/v2/values"
    assert expected_params.data == {"foo": "bar"}
    assert expected_params.headers == {"Content-Type": "application/json; charset=UTF-8"}
    assert expected_params.files is None


def test_default_timeout() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.timeout == con.timeout_put_post, f"Method '{method.__name__}' failed"
    con.get(route="/v2/resources")
    expected_params = con._try_network_action.call_args.args[0]
    assert expected_params.timeout == con.timeout_get, "Method 'GET' failed"


def test_custom_timeout() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.post(route="/v2/resources", timeout=1)
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.timeout == 1


def test_custom_header() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources", headers={"foo": "bar"})
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.headers == {"foo": "bar"}, f"Method '{method.__name__}' failed"


def test_custom_content_type() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources", headers={"Content-Type": "bar"})
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.headers == {"Content-Type": "bar"}, f"Method '{method.__name__}' failed"


def test_server_without_trailing_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


def test_route_without_leading_slash() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


def test_server_and_route_without_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


@patch("dsp_tools.clients.connection_live.log_response")
@patch("dsp_tools.clients.connection_live.log_request")
def test_try_network_action(log_request: Mock, log_response: Mock) -> None:
    con = ConnectionLive("http://example.com/")
    response_expected = Mock(status_code=200)
    con.session.request = Mock(return_value=response_expected)
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    response = con._try_network_action(params)
    assert response == response_expected
    log_request.assert_called_once_with(params, con.session.headers)
    con.session.request.assert_called_once_with(**params.as_kwargs())
    log_response.assert_called_once_with(response_expected)


@patch("dsp_tools.utils.request_utils.log_response")
def test_try_network_action_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (TimeoutError(), ReadTimeout(), Mock(status_code=200))
    session_mock = SessionMock(responses, headers={})
    con.session = session_mock  # type: ignore[assignment]
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    expected_msg = regex.escape("A 'TimeoutError' occurred during the connection to the DSP server.")
    with pytest.raises(PermanentTimeOutError, match=expected_msg):
        con._try_network_action(params)


@patch("dsp_tools.clients.connection_live.log_response")
@patch("dsp_tools.clients.connection_live.log_request")
def test_try_network_action_connection_error(
    log_request: Mock, log_response: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (ConnectionError(), ConnectionError(), RequestException(), Mock(status_code=200))
    session_mock = SessionMock(responses)
    con.session = session_mock  # type: ignore[assignment]
    con._renew_session = Mock()
    params = RequestParameters(method="POST", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.request_utils.time.sleep") as sleep_mock:
        response = con._try_network_action(params)
        assert [x.args[0] for x in sleep_mock.call_args_list] == [1, 2, 4]
    assert con._renew_session.call_count == len(session_mock.responses) - 1
    assert [x.args[0] for x in log_request.call_args_list] == [params] * len(session_mock.responses)
    log_response.assert_called_once_with(session_mock.responses[-1])
    assert response == session_mock.responses[-1]


@patch("dsp_tools.clients.connection_live.log_response")
@patch("dsp_tools.clients.connection_live.log_request")
def test_try_network_action_non_200(log_request: Mock, log_response: Mock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""), Mock(status_code=506, text=""), Mock(status_code=200, text=""))
    session_mock = SessionMock(responses)
    con.session = session_mock  # type: ignore[assignment]
    params = RequestParameters(method="POST", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.request_utils.time.sleep") as sleep_mock:
        response = con._try_network_action(params)
        assert [x.args[0] for x in sleep_mock.call_args_list] == [1, 2]
    assert [x.args[0] for x in log_request.call_args_list] == [params] * len(session_mock.responses)
    assert [x.args[0] for x in log_response.call_args_list] == list(session_mock.responses)
    assert response == session_mock.responses[-1]


@patch("dsp_tools.clients.connection_live.log_response")
@patch("dsp_tools.clients.connection_live.log_request")
def test_try_network_action_in_testing_environment(
    log_request: Mock,  # noqa: ARG001
    log_response: Mock,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DSP_TOOLS_TESTING", "true")  # automatically set in CI, but not locally
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""), Mock(status_code=404, text=""), Mock(status_code=200, text=""))
    con.session = SessionMock(responses, {})  # type: ignore[assignment]
    params = RequestParameters(method="PUT", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.request_utils.log_request_failure_and_sleep") as sleep_mock:
        with pytest.raises(PermanentConnectionError):
            con._try_network_action(params)
        sleep_mock.assert_not_called()


@patch("dsp_tools.clients.connection_live.log_response")
@patch("dsp_tools.clients.connection_live.log_request")
def test_try_network_action_permanent_connection_error(
    log_request: Mock,  # noqa: ARG001
    log_response: Mock,  # noqa: ARG001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DSP_TOOLS_TESTING", "true")  # automatically set in CI, but not locally
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""),) * 7
    con.session = SessionMock(responses, {})  # type: ignore[assignment]
    params = RequestParameters(method="POST", url="http://example.com/", timeout=1)
    with pytest.raises(PermanentConnectionError):
        con._try_network_action(params)


def test_log_request() -> None:
    con = ConnectionLive("http://example.com/")
    con.session.headers = {"Authorization": "Bearer my-very-long-token"}
    params = RequestParameters(
        method="GET",
        url="http://example.com/",
        headers={"request-header": "request-value"},
        timeout=1,
        data={"password": "my-super-secret-password", "foo": "bar"},
    )
    expected_output = {
        "method": "GET",
        "url": "http://example.com/",
        "timeout": 1,
        "headers": {"Authorization": "Bearer ***", "request-header": "request-value"},
        "data": {"password": "***", "foo": "bar"},
    }
    with patch("dsp_tools.utils.request_utils.logger.debug") as debug_mock:
        log_request(params, con.session.headers)
        debug_mock.assert_called_once_with(f"REQUEST: {json.dumps(expected_output)}")


def test_renew_session() -> None:
    con = ConnectionLive("http://example.com/")
    assert con.session.headers["User-Agent"] == f"DSP-TOOLS/{version('dsp-tools')}"
    con._renew_session()
    assert con.session.headers["User-Agent"] == f"DSP-TOOLS/{version('dsp-tools')}"


@pytest.mark.parametrize(
    ("response_content", "expected"),
    [
        (
            '{"message":"Resource class <resclass> does not allow more than one value for property <prop>"}',
            "Resource class <resclass> does not allow more than one value for property <prop>",
        ),
        (
            '{"message":"One or more resources were not found:  <http://rdfh.ch/foo/bar>"}',
            "One or more resources were not found:  <http://rdfh.ch/foo/bar>",
        ),
        (
            '{"message":"Duplicate values for property <http://0.0.0.0:3333/ontology/4124/testonto/v2#hasText>"}',
            "Duplicate values for property <http://0.0.0.0:3333/ontology/4124/testonto/v2#hasText>",
        ),
    ],
)
def test_extract_original_api_err_msg(response_content: str, expected: str) -> None:
    con = ConnectionLive("api")
    assert con._extract_original_api_err_msg(response_content) == expected


@pytest.mark.parametrize(
    ("api_msg", "blame"),
    [
        ("Resource class <resclass> does not allow more than one value for property <prop>", "client"),
        ("One or more resources were not found:  <http://rdfh.ch/foo/bar>", "client"),
        ("Duplicate values for property <http://0.0.0.0:3333/ontology/4124/testonto/v2#hasText>", "client"),
        ("Text value contains invalid characters", "client"),
    ],
)
def test_determine_blame(api_msg: str, blame: Literal["client", "server"]) -> None:
    con = ConnectionLive("api")
    assert con._determine_blame(api_msg) == blame


if __name__ == "__main__":
    pytest.main([__file__])
