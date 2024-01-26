# mypy: disable-error-code="method-assign"

from typing import Any, Callable, cast
from unittest.mock import Mock, patch

import pytest
from requests import ReadTimeout

from dsp_tools.utils.connection_live import ConnectionLive, RequestParameters


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
        assert expected_params.timeout == con.timeout_put_post
    for method in (con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params = con._try_network_action.call_args.args[0]
        assert expected_params.timeout == con.timeout_get_delete


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
        assert expected_params.headers == {"foo": "bar"}


def test_custom_content_type() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources", headers={"Content-Type": "bar"})
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.headers == {"Content-Type": "bar"}


def test_server_without_trailing_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="/v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources"


def test_route_without_leading_slash() -> None:
    con = ConnectionLive("http://example.com/")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources"


def test_server_and_route_without_slash() -> None:
    con = ConnectionLive("http://example.com")
    con._try_network_action = Mock()
    for method in (con.post, con.put, con.get, con.delete):
        method = cast(Callable[..., Any], method)
        method(route="v2/resources")
        expected_params: RequestParameters = con._try_network_action.call_args.args[0]
        assert expected_params.url == "http://example.com/v2/resources"


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
    response_expected = Mock(status_code=200, text="foo")
    con.session.request = Mock(return_value=response_expected)
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    response = con._try_network_action(params)
    assert response == response_expected
    con._log_request.assert_called_once_with(params)
    con.session.request.assert_called_once_with(**params.as_kwargs())
    con._log_response.assert_called_once_with(response_expected)


class SessionMock:
    responses = (TimeoutError(), TimeoutError(), ReadTimeout(), ReadTimeout(), Mock(status_code=200, text="foo"))
    counter = 0

    def request(self, **kwargs: Any) -> Any:  # noqa: ARG002
        response = self.responses[self.counter]
        self.counter += 1
        if isinstance(response, BaseException):
            raise response
        return response


def test_try_network_action_timeout_error() -> None:
    con = ConnectionLive("http://example.com/")
    session_mock = SessionMock()
    con.session = session_mock  # type: ignore[assignment]
    con._log_request = Mock()
    con._log_response = Mock()
    params = RequestParameters(method="GET", url="http://example.com/", timeout=1)
    with patch("dsp_tools.utils.connection_live.time.sleep") as sleep_mock:
        response = con._try_network_action(params)
        assert [x.args[0] for x in sleep_mock.call_args_list] == [1, 2, 4, 8]
    assert [x.args[0] for x in con._log_request.call_args_list] == [params] * len(session_mock.responses)
    con._log_response.assert_called_once_with(session_mock.responses[-1])
    assert response == session_mock.responses[-1]


def test_log_request() -> None:
    pass


def test_log_response() -> None:
    pass


if __name__ == "__main__":
    pytest.main([__file__])
