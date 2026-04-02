from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.exceptions import ProjectOntologyNotFound
from dsp_tools.commands.mapping.mapping_add import _add_classes_mappings
from dsp_tools.commands.mapping.mapping_add import _add_properties_mappings
from dsp_tools.commands.mapping.mapping_add import _communicate_upload_failures
from dsp_tools.commands.mapping.mapping_add import _deal_with_bad_request
from dsp_tools.commands.mapping.mapping_add import _deal_with_non_ok_response
from dsp_tools.commands.mapping.mapping_add import _ontology_exists
from dsp_tools.commands.mapping.models import MappingUploadFailure
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.utils.request_utils import ApiV3ErrorDetails
from dsp_tools.utils.request_utils import ResponseCodeAndText

CLASS_IRI = "http://example.org/onto#Book"
PROP_IRI = "http://example.org/onto#hasTitle"
MAPPING_IRI = "http://schema.org/Book"


class TestOntologyExists:
    def test_ontology_found(self):
        onto_iri = "http://localhost/ontology/0001/myonto/v2"
        with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_cls:
            mock_client = Mock()
            mock_client.get_ontologies.return_value = ([], [onto_iri, "http://other/onto"])
            mock_cls.return_value = mock_client
            assert _ontology_exists("http://localhost", "0001", onto_iri) is True

    def test_ontology_not_found(self):
        with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_cls:
            mock_client = Mock()
            mock_client.get_ontologies.return_value = ([], ["http://other/onto"])
            mock_cls.return_value = mock_client
            assert _ontology_exists("http://localhost", "0001", "http://missing/onto") is False

    def test_project_ontology_not_found_returns_false(self):
        with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_cls:
            mock_client = Mock()
            mock_client.get_ontologies.side_effect = ProjectOntologyNotFound("0001")
            mock_cls.return_value = mock_client
            assert _ontology_exists("http://localhost", "0001", "http://any/onto") is False

    def test_fatal_error_raises_project_not_found(self):
        with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_cls:
            mock_client = Mock()
            mock_client.get_ontologies.side_effect = FatalNonOkApiResponseCode(
                "http://localhost/admin/projects/shortcode/9999", 404, "not found"
            )
            mock_cls.return_value = mock_client
            with pytest.raises(ProjectNotFoundError):
                _ontology_exists("http://localhost", "9999", "http://any/onto")


class TestAddClassesMappings:
    def test_success_returns_no_failures(self):
        client = Mock()
        client.put_class_mapping.return_value = None
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_classes_mappings(client, classes)
        assert result == []

    def test_non_retryable_error_returns_failure(self):
        client = Mock()
        client.put_class_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.BAD_REQUEST,
            text="bad request",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_classes_mappings(client, classes)
        assert len(result) == 1
        assert result[0].iri == CLASS_IRI

    def test_retryable_then_success(self):
        client = Mock()
        client.put_class_mapping.side_effect = [
            ResponseCodeAndText(status_code=500, text="server error"),
            None,
        ]
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.time.sleep"):
            result = _add_classes_mappings(client, classes)
        assert result == []
        assert client.put_class_mapping.call_count == 2

    def test_retryable_then_still_fails(self):
        err_response = ResponseCodeAndText(
            status_code=500,
            text="server error",
        )
        client = Mock()
        client.put_class_mapping.side_effect = [err_response, err_response]
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.time.sleep"):
            result = _add_classes_mappings(client, classes)
        assert len(result) == 1
        assert client.put_class_mapping.call_count == 2


class TestAddPropertiesMappings:
    def test_success_returns_no_failures(self):
        client = Mock()
        client.put_property_mapping.return_value = None
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_properties_mappings(client, props)
        assert result == []

    def test_non_retryable_error_returns_failure(self):
        client = Mock()
        client.put_property_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.BAD_REQUEST,
            text="bad request",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_properties_mappings(client, props)
        assert len(result) == 1
        assert result[0].iri == PROP_IRI

    def test_retryable_then_success(self):
        client = Mock()
        client.put_property_mapping.side_effect = [
            ResponseCodeAndText(status_code=503, text="unavailable"),
            None,
        ]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.time.sleep"):
            result = _add_properties_mappings(client, props)
        assert result == []
        assert client.put_property_mapping.call_count == 2

    def test_retryable_then_still_fails(self):
        err_response = ResponseCodeAndText(status_code=429, text="rate limited")
        client = Mock()
        client.put_property_mapping.side_effect = [err_response, err_response]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.time.sleep"):
            result = _add_properties_mappings(client, props)
        assert len(result) == 1
        assert client.put_property_mapping.call_count == 2


class TestDealWithNonOkResponse:
    def test_400_delegates_to_bad_request(self):
        response = ResponseCodeAndText(
            status_code=HTTPStatus.BAD_REQUEST,
            text="bad",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        result = _deal_with_non_ok_response(CLASS_IRI, response)
        assert len(result) == 1
        assert "class" in result[0].message

    def test_non_400_returns_failure_with_status(self):
        response = ResponseCodeAndText(status_code=503, text="service unavailable")
        result = _deal_with_non_ok_response(CLASS_IRI, response)
        assert len(result) == 1
        assert "503" in result[0].message
        assert CLASS_IRI in result[0].message


class TestDealWithBadRequest:
    def test_no_v3_errors_returns_text_message(self):
        response = ResponseCodeAndText(status_code=400, text="plain error text")
        result = _deal_with_bad_request(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].message == "plain error text"
        assert result[0].mapping_iri is None

    def test_class_not_found(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        result = _deal_with_bad_request(CLASS_IRI, response)
        assert len(result) == 1
        assert CLASS_IRI in result[0].message
        assert result[0].mapping_iri is None

    def test_property_not_found(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        result = _deal_with_bad_request(PROP_IRI, response)
        assert len(result) == 1
        assert PROP_IRI in result[0].message
        assert result[0].mapping_iri is None

    def test_invalid_ontology_mapping_iri(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("invalid_ontology_mapping_iri", "invalid", {"iri": MAPPING_IRI})],
        )
        result = _deal_with_bad_request(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].mapping_iri == MAPPING_IRI
        assert MAPPING_IRI in result[0].message

    def test_unknown_error_code(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("some_unknown_code", "an unknown error", {"key": "val"})],
        )
        result = _deal_with_bad_request(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].mapping_iri is None
        assert "an unknown error" in result[0].message


class TestCommunicateUploadFailures:
    def test_without_mapping_iri(self, capsys):
        failures = [MappingUploadFailure(iri=CLASS_IRI, mapping_iri=None, message="class not found")]
        _communicate_upload_failures(failures)
        out = capsys.readouterr().out
        assert CLASS_IRI in out
        assert "class not found" in out

    def test_with_mapping_iri(self, capsys):
        failures = [MappingUploadFailure(iri=CLASS_IRI, mapping_iri=MAPPING_IRI, message="invalid IRI")]
        _communicate_upload_failures(failures)
        out = capsys.readouterr().out
        assert CLASS_IRI in out
        assert MAPPING_IRI in out
        assert "invalid IRI" in out
