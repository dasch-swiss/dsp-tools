from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.exceptions import ProjectOntologyNotFound
from dsp_tools.commands.mapping.exceptions import OntologyReferencedNotFoundError
from dsp_tools.commands.mapping.mapping_add import _add_classes_mappings
from dsp_tools.commands.mapping.mapping_add import _add_properties_mappings
from dsp_tools.commands.mapping.mapping_add import _check_if_project_and_ontology_exists
from dsp_tools.commands.mapping.mapping_add import _get_correct_user_message_for_non_ok_response
from dsp_tools.commands.mapping.mapping_add import _get_detailed_user_message
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.utils.request_utils import ApiV3ErrorDetails
from dsp_tools.utils.request_utils import ResponseCodeAndText

ONTO_NAME = "onto"
SHORTCODE = "0001"
ONTO_IRI = f"http://0.0.0.0:3333/ontology/{SHORTCODE}/{ONTO_NAME}/v2"

CLASS_IRI = f"{ONTO_IRI}#Book"
PREFIXED_CLS = f"{ONTO_NAME}:Book"

PROP_IRI = f"{ONTO_IRI}#hasTitle"
PREFIXED_PROP = f"{ONTO_NAME}:hasTitle"

MAPPING_IRI = "http://schema.org/Book"

MAPPING_CONFIG = MappingConfig(shortcode=SHORTCODE, ontology=ONTO_NAME, excel_file=Path("dummy.xlsx"))


class TestOntologyExists:
    def _make_auth(self) -> Mock:
        auth = Mock()
        auth.server = "http://0.0.0.0:3333"
        return auth

    def test_ontology_found(self):
        with patch("dsp_tools.commands.mapping.mapping_add.ProjectClientLive") as mock_project_cls:
            mock_project_client = Mock()
            mock_project_cls.return_value = mock_project_client
            with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.return_value = ([], [ONTO_IRI, "http://other/onto"])
                mock_onto_cls.return_value = mock_onto_client
                result = _check_if_project_and_ontology_exists(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)
        assert result is None

    def test_ontology_not_found_raises(self):
        with patch("dsp_tools.commands.mapping.mapping_add.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.return_value = ([], ["http://other/onto"])
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(OntologyReferencedNotFoundError):
                    _check_if_project_and_ontology_exists(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)

    def test_project_not_found_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_add.ProjectClientLive") as mock_project_cls:
            mock_project_client = Mock()
            mock_project_client.get_project_iri.side_effect = ProjectNotFoundError("0001")
            mock_project_cls.return_value = mock_project_client
            with pytest.raises(ProjectNotFoundError):
                _check_if_project_and_ontology_exists(
                    self._make_auth(), MAPPING_CONFIG, "http://localhost/ontology/0001/myonto/v2"
                )

    def test_get_ontologies_project_not_found_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_add.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.side_effect = ProjectOntologyNotFound("0001")
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(ProjectOntologyNotFound):
                    _check_if_project_and_ontology_exists(
                        self._make_auth(), MAPPING_CONFIG, "http://localhost/ontology/0001/myonto/v2"
                    )

    def test_get_ontologies_fatal_error_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_add.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_add.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.side_effect = FatalNonOkApiResponseCode(
                    "http://localhost/ontology/0001/myonto/v2", 500, "server error"
                )
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(FatalNonOkApiResponseCode):
                    _check_if_project_and_ontology_exists(
                        self._make_auth(), MAPPING_CONFIG, "http://localhost/ontology/0001/myonto/v2"
                    )


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
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == f"The class '{PREFIXED_CLS}' was not found in the ontology on the server."

    def test_retryable_then_success(self):
        client = Mock()
        client.put_class_mapping.side_effect = [
            ResponseCodeAndText(status_code=500, text="server error"),
            None,
        ]
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.should_retry_request", return_value=True):
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
        with patch("dsp_tools.commands.mapping.mapping_add.should_retry_request", return_value=True):
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
        assert result[0].prefixed_iri == PREFIXED_PROP
        assert result[0].mapping_iri is None
        assert result[0].message == "The property 'onto:hasTitle' was not found in the ontology on the server."

    def test_retryable_then_success(self):
        client = Mock()
        client.put_property_mapping.side_effect = [
            ResponseCodeAndText(status_code=503, text="unavailable"),
            None,
        ]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_add.time.sleep"):
                result = _add_properties_mappings(client, props)
        assert result == []
        assert client.put_property_mapping.call_count == 2

    def test_retryable_then_still_fails(self):
        err_response = ResponseCodeAndText(status_code=429, text="rate limited")
        client = Mock()
        client.put_property_mapping.side_effect = [err_response, err_response]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_add.should_retry_request", return_value=True):
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
        result = _get_correct_user_message_for_non_ok_response(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "The class 'onto:Book' was not found in the ontology on the server."

    def test_non_400_returns_failure_with_status(self):
        response = ResponseCodeAndText(status_code=503, text="service unavailable")
        result = _get_correct_user_message_for_non_ok_response(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == (
            "Unexpected error while adding mapping for class/property 'onto:Book'. "
            "Original status code: 503\n"
            "Original message: service unavailable"
        )


class TestDealWithBadRequest:
    def test_no_v3_errors_returns_text_message(self):
        response = ResponseCodeAndText(status_code=400, text="plain error text")
        result = _get_detailed_user_message(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "plain error text"

    def test_class_not_found(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "The class 'onto:Book' was not found in the ontology on the server."

    def test_property_not_found(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        result = _get_detailed_user_message(PROP_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_PROP
        assert result[0].mapping_iri is None
        assert result[0].message == "The property 'onto:hasTitle' was not found in the ontology on the server."

    def test_invalid_ontology_mapping_iri(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("invalid_ontology_mapping_iri", "invalid", {"iri": "invalid-text"})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri == "invalid-text"
        assert result[0].message == "The mapping IRI 'invalid-text' is not a valid external ontology IRI."

    def test_unknown_error_code(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("some_unknown_code", "an unknown error", {})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "an unknown error"
