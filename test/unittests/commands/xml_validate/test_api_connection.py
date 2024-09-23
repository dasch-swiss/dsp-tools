from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.xml_validate.api_connection import Authentication
from dsp_tools.commands.xml_validate.api_connection import OntologyConnection
from dsp_tools.models.exceptions import InternalError
from dsp_tools.models.exceptions import UserError


@pytest.fixture
def ontology_connection() -> OntologyConnection:
    return OntologyConnection("http://example.com", "9999")


class TestAuthentication:
    def test_ok(self) -> None:
        auth = Authentication("http://example.com", "email@test.ch", "pw1234")
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"token": "token"}
        with patch.object(auth, "_request_token", return_value=mock_response):
            expected_tkn = "Bearer token"
            assert auth.get_bearer_token() == expected_tkn
            assert auth.bearer_tkn == expected_tkn

    def test_non_ok_code(self) -> None:
        auth = Authentication("http://example.com", "email@test.ch", "pw1234")
        mock_response = Mock()
        mock_response.ok = False
        with patch.object(auth, "_request_token", return_value=mock_response):
            with pytest.raises(UserError):
                auth.get_bearer_token()

    def test_no_token(self) -> None:
        auth = Authentication("http://example.com", "email@test.ch", "pw1234")
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"other": "other"}
        with patch.object(auth, "_request_token", return_value=mock_response):
            with pytest.raises(InternalError):
                auth.get_bearer_token()


class TestOntologyConnection:
    def test_get_ontology_iris_ok(self, ontology_connection: OntologyConnection) -> None:
        pass

    def test_get_ontology_iris_non_ok_code(self, ontology_connection: OntologyConnection) -> None:
        pass


if __name__ == "__main__":
    pytest.main([__file__])
