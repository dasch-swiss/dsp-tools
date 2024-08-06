# mypy: disable-error-code="method-assign"

import json
from dataclasses import dataclass
from importlib.metadata import version
from typing import Any
from typing import Callable
from typing import cast
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import regex
from requests import ReadTimeout
from requests import RequestException

from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.connection_live import RequestParameters


@dataclass
class SessionMock:
    responses: tuple[Any, ...]
    counter = 0

    def request(self, **kwargs: Any) -> Any:  # noqa: ARG002
        response = self.responses[self.counter]
        self.counter += 1
        if isinstance(response, BaseException):
            raise response
        return response


@dataclass
class ResponseMock:
    status_code: int
    headers: dict[str, Any]
    text: str


def test_log_in_log_out() -> None:
    con = ConnectionLive("http://example.com/")
    con.post = Mock(return_value={"token": "token"})
    con.login("root@example.com", "test")
    assert con.post.call_args.kwargs["route"] == "/v2/authentication"
    assert con.token == "token"
    assert con.session.headers["Authorization"] == "Bearer token"
    con.delete = Mock()
    con.logout()
    assert con.token is None
    assert "Authorization" not in con.session.headers


def test_log_in_bad_credentials() -> None:
    con = ConnectionLive("http://example.com/")
    con._log_response = Mock()
    con.session.request = Mock(return_value=Mock(status_code=401))
    with patch("dsp_tools.utils.connection_live.time.sleep") as sleep_mock:
        with pytest.raises(UserError, match=regex.escape("Username and/or password are not valid")):
            con.login("invalid@example.com", "wrong")
        sleep_mock.assert_not_called()


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
    file = {"file": ("path/to/file.jpg", b"some bytes")}
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


def test_delete() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.delete(route="/v2/values")
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.method == "DELETE"
    assert expected_params.url == "http://example.com/v2/values"
    assert expected_params.data is None
    assert expected_params.headers is None
    assert expected_params.files is None


def test_default_timeout() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.timeout == con.timeout_put_post, f"Method '{method.__name__}' failed"
    for method in (con.get, con.delete):  # type: ignore[assignment]
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params = con._try_network_action.call_args.args[0]
        assert expected_params.timeout == con.timeout_get_delete, f"Method '{method.__name__}' failed"


def test_custom_timeout() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    con.post(route="/v2/resources", timeout=1)
    expected_params: RequestParameters = con._try_network_action.call_args.args[0]
    assert expected_params.timeout == 1


def test_custom_header() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources", headers={"foo": "bar"})
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.headers == {"foo": "bar"}, f"Method '{method.__name__}' failed"


def test_custom_content_type() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources", headers={"Content-Type": "bar"})
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.headers == {"Content-Type": "bar"}, f"Method '{method.__name__}' failed"


def test_server_without_trailing_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


def test_route_without_leading_slash() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


def test_server_and_route_without_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources", f"Method '{method.__name__}' failed"


def test_anonymize_different_keys() -> None:
    con = ConnectionLive("foo")
    assert con._anonymize(None) is None
    assert con._anonymize({"foo": "bar"}) == {"foo": "bar"}
    assert con._anonymize({"token": "uk7m20-8gqn8"}) == {"token": "uk7m2[+7]"}
    assert con._anonymize({"Set-Cookie": "uk7m20-8gqn8"}) == {"Set-Cookie": "uk7m2[+7]"}
    assert con._anonymize({"Authorization": "Bearer uk7m20-8gqn8"}) == {"Authorization": "Bearer uk7m2[+7]"}
    assert con._anonymize({"password": "uk7m20-8gqn8"}) == {"password": "************"}


def test_anonymize_doesnt_mutate_original() -> None:
    con = ConnectionLive("foo")
    random = {"foo": "bar"}
    assert con._anonymize(random) is not random


def test_anonymize_different_lengths() -> None:
    con = ConnectionLive("foo")
    assert con._anonymize({"token": "uk7m20-8gqn8ir7e30"}) == {"token": "uk7m2[+13]"}
    assert con._anonymize({"token": "uk7m2"}) == {"token": "*****"}
    assert con._anonymize({"token": "u"}) == {"token": "*"}


def test_try_network_action() -> None:
    con = ConnectionLive("http://example.com/")
    response_expected = Mock(status_code=200)
    con.session.request = Mock(return_value=response_expected)
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    response = con._try_network_action(params)
    assert response == response_expected
    con._log_request.assert_called_once_with(params)
    con.session.request.assert_called_once_with(**params.as_kwargs())
    con._log_response.assert_called_once_with(response_expected)


def test_try_network_action_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (TimeoutError(), ReadTimeout(), Mock(status_code=200))
    session_mock = SessionMock(responses)
    con.session = session_mock  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    expected_msg = regex.escape("A 'TimeoutError' occurred during the connection to the DSP server.")
    with pytest.raises(PermanentTimeOutError, match=expected_msg):
        con._try_network_action(params)


def test_try_network_action_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (ConnectionError(), ConnectionError(), RequestException(), Mock(status_code=200))
    session_mock = SessionMock(responses)
    con.session = session_mock  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
    con._renew_session = Mock()
    params = RequestParameters(method="POST", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.connection_live.time.sleep") as sleep_mock:
        response = con._try_network_action(params)
        assert [x.args[0] for x in sleep_mock.call_args_list] == [1, 2, 4]
    assert con._renew_session.call_count == len(session_mock.responses) - 1
    assert [x.args[0] for x in con._log_request.call_args_list] == [params] * len(session_mock.responses)
    con._log_response.assert_called_once_with(session_mock.responses[-1])
    assert response == session_mock.responses[-1]


def test_try_network_action_non_200(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)  # in CI, this variable suppresses the retrying mechanism
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""), Mock(status_code=506, text=""), Mock(status_code=200, text=""))
    session_mock = SessionMock(responses)
    con.session = session_mock  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="POST", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.connection_live.time.sleep") as sleep_mock:
        response = con._try_network_action(params)
        assert [x.args[0] for x in sleep_mock.call_args_list] == [1, 2]
    assert [x.args[0] for x in con._log_request.call_args_list] == [params] * len(session_mock.responses)
    assert [x.args[0] for x in con._log_response.call_args_list] == list(session_mock.responses)
    assert response == session_mock.responses[-1]


def test_try_network_action_in_testing_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSP_TOOLS_TESTING", "true")  # automatically set in CI, but not locally
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""), Mock(status_code=404, text=""), Mock(status_code=200, text=""))
    con.session = SessionMock(responses)  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="PUT", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.connection_live.time.sleep") as sleep_mock:
        with pytest.raises(PermanentConnectionError):
            con._try_network_action(params)
        sleep_mock.assert_not_called()


def test_try_network_action_permanent_connection_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DSP_TOOLS_TESTING", "true")  # automatically set in CI, but not locally
    con = ConnectionLive("http://example.com/")
    responses = (Mock(status_code=500, text=""),) * 7
    con.session = SessionMock(responses)  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
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
        "headers": {"Authorization": "Bearer my-ve[+13]", "request-header": "request-value"},
        "timeout": 1,
        "data": {"password": "************************", "foo": "bar"},
    }
    with patch("dsp_tools.utils.connection_live.logger.debug") as debug_mock:
        con._log_request(params)
        debug_mock.assert_called_once_with(f"REQUEST: {json.dumps(expected_output)}")


def test_log_response() -> None:
    con = ConnectionLive("http://example.com/")
    response_mock = ResponseMock(
        status_code=200,
        headers={"Set-Cookie": "KnoraAuthenticationMFYGSLT", "Content-Type": "application/json"},
        text=json.dumps({"token": "my-very-long-token", "foo": "bar"}),
    )
    expected_output = {
        "status_code": 200,
        "headers": {"Set-Cookie": "Knora[+21]", "Content-Type": "application/json"},
        "content": {"token": "my-ve[+13]", "foo": "bar"},
    }
    with patch("dsp_tools.utils.connection_live.logger.debug") as debug_mock:
        con._log_response(response_mock)  # type: ignore[arg-type]
        debug_mock.assert_called_once_with(f"RESPONSE: {json.dumps(expected_output)}")


def test_renew_session() -> None:
    con = ConnectionLive("http://example.com/", "my-super-secret-token")
    assert con.get_token() == "my-super-secret-token"
    assert con.session.headers["User-Agent"] == f'DSP-TOOLS/{version("dsp-tools")}'
    con._renew_session()
    assert con.get_token() == "my-super-secret-token"
    assert con.session.headers["User-Agent"] == f'DSP-TOOLS/{version("dsp-tools")}'


if __name__ == "__main__":
    pytest.main([__file__])
