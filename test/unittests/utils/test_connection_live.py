from unittest.mock import Mock

import pytest

from dsp_tools.utils.connection_live import ConnectionLive


def test_log_in_log_out() -> None:
    con = ConnectionLive("http://example.com/")
    con.post = Mock(return_value={"token": "token"})  # type: ignore[method-assign]
    con.login("root@example.com", "test")
    assert con.token == "token"
    assert con.session.headers["Authorization"] == "Bearer token"
    con.delete = Mock()  # type: ignore[method-assign]
    con.logout()
    assert con.token is None
    assert "Authorization" not in con.session.headers


def test_post() -> None:
    con = ConnectionLive("http://example.com/")
    con._anonymize = Mock(side_effect=lambda x: x)  # type: ignore[method-assign]
    con._log_response = Mock()  # type: ignore[method-assign]
    con._should_retry = Mock(return_value=False)  # type: ignore[method-assign]
    response_mock = Mock()
    response_mock.status_code = 200
    post_mock = Mock(return_value=response_mock)
    con.session.post = post_mock  # type: ignore[method-assign]
    con.session.headers = {}
    con.post(route="/v2/resources", data={"foo": "bar"})
    post_mock.assert_called_once_with(
        url="http://example.com/v2/resources",
        headers={"Content-Type": "application/json; charset=UTF-8"},
        timeout=con.timeout_put_post,
        data=b'{"foo": "bar"}',
        files=None,
    )


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


if __name__ == "__main__":
    pytest.main([__file__])
