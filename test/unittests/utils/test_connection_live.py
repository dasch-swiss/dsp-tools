from unittest.mock import Mock

import pytest

from dsp_tools.utils.connection_live import ConnectionLive


def test_log_in_log_out() -> None:
    con = ConnectionLive("http://example.com/")
    con.post = Mock(return_value={"token": "token"})  # type: ignore[method-assign]
    con.login("root@example.com", "test")
    assert con.token == "token"
    con.post.assert_called_once_with(route="/v2/authentication", data={"email": "root@example.com", "password": "test"})
    con.delete = Mock()  # type: ignore[method-assign]
    con.logout()
    assert con.token is None
    con.delete.assert_called_once_with(route="/v2/authentication")


def test_anonymize_different_keys() -> None:
    con = ConnectionLive("foo")
    assert con._anonymize(None) is None
    assert con._anonymize({"foo": "bar"}) == {"foo": "bar"}
    assert con._anonymize({"token": "uk7m20-8gqn8"}) == {"token": "uk7m2[+7]"}
    assert con._anonymize({"Set-Cookie": "uk7m20-8gqn8"}) == {"Set-Cookie": "uk7m2[+7]"}
    assert con._anonymize({"Authorization": "Bearer uk7m20-8gqn8"}) == {"Authorization": "Bearer uk7m2[+7]"}
    assert con._anonymize({"password": "uk7m20-8gqn8"}) == {"password": "uk7m2[+7]"}


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
