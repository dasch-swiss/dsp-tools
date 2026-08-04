import json
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch
from urllib.parse import quote_plus

import pytest
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.request_utils import ResponseCodeAndText

AUTH = Mock()
AUTH.get_token = Mock(return_value="test-token")

SERVER = "http://localhost:3333"
ONTO_IRI = "http://localhost:3333/ontology/0001/my-onto/v2"
CLASS_IRI = "http://localhost:3333/ontology/0001/my-onto/v2#Book"
PROP_IRI = "http://localhost:3333/ontology/0001/my-onto/v2#hasTitle"
MAPPING_IRI = "http://schema.org/Book"

ENCODED_ONTO_IRI = quote_plus(ONTO_IRI)


def _make_client() -> MappingClientLive:
    return MappingClientLive(server=SERVER, encoded_ontology_iri=ENCODED_ONTO_IRI, auth=AUTH)


def _make_response_mock(status_code: int, body: dict[str, Any] | str) -> Mock:
    mock = Mock()
    mock.status_code = status_code
    mock.headers = {"Content-Type": "application/json"}
    if isinstance(body, dict):
        mock.text = json.dumps(body)
        mock.json.return_value = body
    else:
        mock.text = body
        mock.json.side_effect = RequestsJSONDecodeError("no json", "", 0)
    return mock


class TestMappingClientLivePut:
    def test_put_class_mapping_success_returns_none(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        assert result is None

    def test_put_class_mapping_bad_request_returns_response_code_and_text(self):
        body = {"errors": [{"code": "class_not_found", "message": "not found", "details": {}}]}
        mock_response = _make_response_mock(400, body)
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 400
        assert result.v3_errors is not None
        assert result.v3_errors[0].error_code == "class_not_found"

    def test_put_class_mapping_forbidden_raises_bad_credentials(self):
        mock_response = _make_response_mock(403, "forbidden")
        with patch("requests.put", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])

    def test_put_class_mapping_server_error_returns_response_code_and_text(self):
        mock_response = _make_response_mock(500, "internal server error")
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 500
        assert result.v3_errors is None

    def test_put_class_mapping_non_json_body_returns_v3_errors_none(self):
        mock_response = _make_response_mock(400, "plain text error")
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.v3_errors is None

    def test_put_class_mapping_url_contains_encoded_iris(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        call_kwargs = mock_put.call_args
        url = call_kwargs.kwargs["url"]
        assert ENCODED_ONTO_IRI in url
        assert quote_plus(CLASS_IRI) in url

    def test_put_class_mapping_authorization_header(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        headers = mock_put.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test-token"

    def test_put_class_mapping_body_contains_mappings(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_class_mapping(CLASS_IRI, [MAPPING_IRI])
        data = json.loads(mock_put.call_args.kwargs["data"])
        assert data == {"mappings": [MAPPING_IRI]}

    def test_put_property_mapping_success_returns_none(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        assert result is None

    def test_put_property_mapping_bad_request_returns_response_code_and_text(self):
        body = {"errors": [{"code": "property_not_found", "message": "not found", "details": {}}]}
        mock_response = _make_response_mock(400, body)
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.v3_errors is not None
        assert result.v3_errors[0].error_code == "property_not_found"

    def test_put_property_mapping_forbidden_raises_bad_credentials(self):
        mock_response = _make_response_mock(403, "forbidden")
        with patch("requests.put", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])

    def test_put_property_mapping_server_error_returns_response_code_and_text(self):
        mock_response = _make_response_mock(500, "internal server error")
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 500

    def test_put_property_mapping_non_json_body_returns_v3_errors_none(self):
        mock_response = _make_response_mock(400, "plain text error")
        with patch("requests.put", return_value=mock_response):
            result = _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        assert isinstance(result, ResponseCodeAndText)
        assert result.v3_errors is None

    def test_put_property_mapping_url_contains_encoded_iris(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        url = mock_put.call_args.kwargs["url"]
        assert ENCODED_ONTO_IRI in url
        assert quote_plus(PROP_IRI) in url

    def test_put_property_mapping_authorization_header(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        headers = mock_put.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test-token"

    def test_put_property_mapping_body_contains_mappings(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.put", return_value=mock_response) as mock_put:
            _make_client().put_property_mapping(PROP_IRI, [MAPPING_IRI])
        data = json.loads(mock_put.call_args.kwargs["data"])
        assert data == {"mappings": [MAPPING_IRI]}


class TestMappingClientLiveDelete:
    def test_delete_class_mapping_success_returns_none(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        assert result is None

    def test_delete_class_mapping_bad_request_returns_response_code_and_text(self):
        body = {"errors": [{"code": "invalid_ontology_mapping_iri", "message": "invalid", "details": {"iri": "nope"}}]}
        mock_response = _make_response_mock(400, body)
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 400
        assert result.v3_errors is not None
        assert result.v3_errors[0].error_code == "invalid_ontology_mapping_iri"
        assert result.v3_errors[0].details == {"iri": "nope"}

    def test_delete_class_mapping_forbidden_raises_bad_credentials(self):
        mock_response = _make_response_mock(403, "forbidden")
        with patch("requests.delete", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)

    def test_delete_class_mapping_server_error_returns_response_code_and_text(self):
        mock_response = _make_response_mock(500, "internal server error")
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 500
        assert result.v3_errors is None

    def test_delete_class_mapping_url_contains_encoded_iris(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        url = mock_delete.call_args.kwargs["url"]
        assert ENCODED_ONTO_IRI in url
        assert quote_plus(CLASS_IRI) in url
        assert url.endswith(f"?mapping={quote_plus(MAPPING_IRI)}")

    def test_delete_class_mapping_authorization_header(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        headers = mock_delete.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test-token"

    def test_delete_class_mapping_encodes_fragment_in_mapping_iri(self):
        # A raw '#' would be treated as a client-side fragment and never reach the server.
        mapping_with_fragment = "http://www.w3.org/ns/prov#Entity"
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_class_mapping(CLASS_IRI, mapping_with_fragment)
        url = mock_delete.call_args.kwargs["url"]
        assert f"mapping={quote_plus(mapping_with_fragment)}" in url
        assert "#" not in url

    def test_delete_property_mapping_success_returns_none(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)
        assert result is None

    def test_delete_property_mapping_bad_request_returns_response_code_and_text(self):
        body = {"errors": [{"code": "property_not_found", "message": "not found", "details": {}}]}
        mock_response = _make_response_mock(400, body)
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)
        assert isinstance(result, ResponseCodeAndText)
        assert result.v3_errors is not None
        assert result.v3_errors[0].error_code == "property_not_found"

    def test_delete_property_mapping_forbidden_raises_bad_credentials(self):
        mock_response = _make_response_mock(403, "forbidden")
        with patch("requests.delete", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)

    def test_delete_property_mapping_server_error_returns_response_code_and_text(self):
        mock_response = _make_response_mock(500, "internal server error")
        with patch("requests.delete", return_value=mock_response):
            result = _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 500

    def test_delete_property_mapping_url_contains_encoded_iris(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)
        url = mock_delete.call_args.kwargs["url"]
        assert ENCODED_ONTO_IRI in url
        assert quote_plus(PROP_IRI) in url
        assert url.endswith(f"?mapping={quote_plus(MAPPING_IRI)}")

    def test_delete_property_mapping_authorization_header(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_property_mapping(PROP_IRI, MAPPING_IRI)
        headers = mock_delete.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer test-token"

    def test_delete_sends_no_body(self):
        mock_response = _make_response_mock(200, {})
        with patch("requests.delete", return_value=mock_response) as mock_delete:
            _make_client().delete_class_mapping(CLASS_IRI, MAPPING_IRI)
        assert "data" not in mock_delete.call_args.kwargs
        assert "Content-Type" not in mock_delete.call_args.kwargs["headers"]
