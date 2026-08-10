from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.exceptions import ProjectOntologyNotFound
from dsp_tools.commands.mapping.exceptions import OntologyReferencedNotFoundError
from dsp_tools.commands.mapping.mapping_update import RERUN_ADVICE
from dsp_tools.commands.mapping.mapping_update import _add_classes_mappings
from dsp_tools.commands.mapping.mapping_update import _add_properties_mappings
from dsp_tools.commands.mapping.mapping_update import _check_project_and_get_ontology_ttl
from dsp_tools.commands.mapping.mapping_update import _communicate_planned_deletions
from dsp_tools.commands.mapping.mapping_update import _communicate_upload_failures
from dsp_tools.commands.mapping.mapping_update import _delete_class_mappings
from dsp_tools.commands.mapping.mapping_update import _delete_property_mappings
from dsp_tools.commands.mapping.mapping_update import _get_correct_user_message_for_non_ok_response
from dsp_tools.commands.mapping.mapping_update import _get_detailed_user_message
from dsp_tools.commands.mapping.models import MappingAction
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import MappingDeletion
from dsp_tools.commands.mapping.models import MappingDeletions
from dsp_tools.commands.mapping.models import MappingUploadFailure
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

TARGET_TTL = "<target> a <Ontology> ."
OTHER_TTL = "<other> a <Ontology> ."
OTHER_IRI = "http://other/onto"


class TestCheckProjectAndGetOntologyTtl:
    def _make_auth(self) -> Mock:
        auth = Mock()
        auth.server = "http://0.0.0.0:3333"
        return auth

    def test_ontology_found_returns_its_turtle(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_update.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.return_value = ([TARGET_TTL, OTHER_TTL], [ONTO_IRI, OTHER_IRI])
                mock_onto_cls.return_value = mock_onto_client
                result = _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)
        assert result == TARGET_TTL

    def test_turtle_is_selected_by_index_not_by_position(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_update.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.return_value = ([OTHER_TTL, TARGET_TTL], [OTHER_IRI, ONTO_IRI])
                mock_onto_cls.return_value = mock_onto_client
                result = _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)
        assert result == TARGET_TTL

    def test_ontology_not_found_raises(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_update.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.return_value = ([OTHER_TTL], [OTHER_IRI])
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(OntologyReferencedNotFoundError):
                    _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)

    def test_project_not_found_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_client = Mock()
            mock_project_client.get_project_iri.side_effect = ProjectNotFoundError("0001")
            mock_project_cls.return_value = mock_project_client
            with pytest.raises(ProjectNotFoundError):
                _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)

    def test_get_ontologies_project_not_found_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_update.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.side_effect = ProjectOntologyNotFound("0001")
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(ProjectOntologyNotFound):
                    _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)

    def test_get_ontologies_fatal_error_propagates(self):
        with patch("dsp_tools.commands.mapping.mapping_update.ProjectClientLive") as mock_project_cls:
            mock_project_cls.return_value = Mock()
            with patch("dsp_tools.commands.mapping.mapping_update.OntologyGetClientLive") as mock_onto_cls:
                mock_onto_client = Mock()
                mock_onto_client.get_ontologies.side_effect = FatalNonOkApiResponseCode(ONTO_IRI, 500, "server error")
                mock_onto_cls.return_value = mock_onto_client
                with pytest.raises(FatalNonOkApiResponseCode):
                    _check_project_and_get_ontology_ttl(self._make_auth(), MAPPING_CONFIG, ONTO_IRI)


class TestAddClassesMappings:
    def test_success_returns_no_failures(self):
        client = Mock()
        client.put_class_mapping.return_value = None
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_classes_mappings(client, classes)
        assert result == []

    def test_empty_list_sends_nothing(self):
        client = Mock()
        result = _add_classes_mappings(client, [])
        assert result == []
        assert client.put_class_mapping.call_count == 0

    def test_non_retryable_error_returns_failure(self):
        client = Mock()
        client.put_class_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="not found",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_classes_mappings(client, classes)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].action is MappingAction.ADD
        assert result[0].message == f"The class '{PREFIXED_CLS}' was not found in the ontology on the server."

    def test_retryable_then_success(self):
        client = Mock()
        client.put_class_mapping.side_effect = [
            ResponseCodeAndText(status_code=500, text="server error"),
            None,
        ]
        classes = [ResolvedClassMapping(iri=CLASS_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
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
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
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

    def test_empty_list_sends_nothing(self):
        client = Mock()
        result = _add_properties_mappings(client, [])
        assert result == []
        assert client.put_property_mapping.call_count == 0

    def test_non_retryable_error_returns_failure(self):
        client = Mock()
        client.put_property_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="not found",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        result = _add_properties_mappings(client, props)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_PROP
        assert result[0].mapping_iri is None
        assert result[0].action is MappingAction.ADD
        assert result[0].message == "The property 'onto:hasTitle' was not found in the ontology on the server."

    def test_retryable_then_success(self):
        client = Mock()
        client.put_property_mapping.side_effect = [
            ResponseCodeAndText(status_code=503, text="unavailable"),
            None,
        ]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
                result = _add_properties_mappings(client, props)
        assert result == []
        assert client.put_property_mapping.call_count == 2

    def test_retryable_then_still_fails(self):
        err_response = ResponseCodeAndText(status_code=429, text="rate limited")
        client = Mock()
        client.put_property_mapping.side_effect = [err_response, err_response]
        props = [ResolvedPropertyMapping(iri=PROP_IRI, mapping_iris=[MAPPING_IRI])]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
                result = _add_properties_mappings(client, props)
        assert len(result) == 1
        assert client.put_property_mapping.call_count == 2


class TestDeleteClassMappings:
    def test_success_returns_no_failures(self):
        client = Mock()
        client.delete_class_mapping.return_value = None
        deletions = [MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI)]
        result = _delete_class_mappings(client, deletions)
        assert result == []
        assert client.delete_class_mapping.call_count == 1

    def test_empty_list_sends_nothing(self):
        client = Mock()
        result = _delete_class_mappings(client, [])
        assert result == []
        assert client.delete_class_mapping.call_count == 0

    def test_non_retryable_error_names_the_mapping_iri(self):
        client = Mock()
        client.delete_class_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="not found",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        deletions = [MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI)]
        result = _delete_class_mappings(client, deletions)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri == MAPPING_IRI
        assert result[0].action is MappingAction.DELETE
        assert result[0].message == f"The class '{PREFIXED_CLS}' was not found in the ontology on the server."

    def test_retryable_then_success(self):
        client = Mock()
        client.delete_class_mapping.side_effect = [
            ResponseCodeAndText(status_code=500, text="server error"),
            None,
        ]
        deletions = [MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI)]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
                result = _delete_class_mappings(client, deletions)
        assert result == []
        assert client.delete_class_mapping.call_count == 2

    def test_retryable_then_still_fails(self):
        err_response = ResponseCodeAndText(status_code=500, text="server error")
        client = Mock()
        client.delete_class_mapping.side_effect = [err_response, err_response]
        deletions = [MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI)]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
                result = _delete_class_mappings(client, deletions)
        assert len(result) == 1
        assert result[0].action is MappingAction.DELETE
        assert client.delete_class_mapping.call_count == 2

    def test_one_request_per_mapping_iri(self):
        client = Mock()
        client.delete_class_mapping.return_value = None
        deletions = [
            MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI),
            MappingDeletion(entity_iri=CLASS_IRI, mapping_iri="http://purl.org/ontology/bibo/Book"),
        ]
        _delete_class_mappings(client, deletions)
        assert client.delete_class_mapping.call_count == 2


class TestDeletePropertyMappings:
    def test_success_returns_no_failures(self):
        client = Mock()
        client.delete_property_mapping.return_value = None
        deletions = [MappingDeletion(entity_iri=PROP_IRI, mapping_iri=MAPPING_IRI)]
        result = _delete_property_mappings(client, deletions)
        assert result == []

    def test_empty_list_sends_nothing(self):
        client = Mock()
        result = _delete_property_mappings(client, [])
        assert result == []
        assert client.delete_property_mapping.call_count == 0

    def test_non_retryable_error_names_the_mapping_iri(self):
        client = Mock()
        client.delete_property_mapping.return_value = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="not found",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        deletions = [MappingDeletion(entity_iri=PROP_IRI, mapping_iri=MAPPING_IRI)]
        result = _delete_property_mappings(client, deletions)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_PROP
        assert result[0].mapping_iri == MAPPING_IRI
        assert result[0].action is MappingAction.DELETE

    def test_retryable_then_success(self):
        client = Mock()
        client.delete_property_mapping.side_effect = [
            ResponseCodeAndText(status_code=503, text="unavailable"),
            None,
        ]
        deletions = [MappingDeletion(entity_iri=PROP_IRI, mapping_iri=MAPPING_IRI)]
        with patch("dsp_tools.commands.mapping.mapping_update.should_retry_request", return_value=True):
            with patch("dsp_tools.commands.mapping.mapping_update.time.sleep"):
                result = _delete_property_mappings(client, deletions)
        assert result == []
        assert client.delete_property_mapping.call_count == 2


class TestDealWithNonOkResponse:
    def test_400_delegates_to_bad_request(self):
        response = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="not found",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        result = _get_correct_user_message_for_non_ok_response(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].action is MappingAction.ADD
        assert result[0].message == "The class 'onto:Book' was not found in the ontology on the server."

    def test_non_400_returns_failure_with_status(self):
        response = ResponseCodeAndText(status_code=503, text="service unavailable")
        result = _get_correct_user_message_for_non_ok_response(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == (
            "Unexpected error while trying to add the mapping for class/property 'onto:Book'. "
            "Original status code: 503\n"
            "Original message: service unavailable"
        )

    def test_non_400_delete_wording_and_mapping_iri(self):
        response = ResponseCodeAndText(status_code=503, text="service unavailable")
        result = _get_correct_user_message_for_non_ok_response(CLASS_IRI, response, MappingAction.DELETE, MAPPING_IRI)
        assert len(result) == 1
        assert result[0].mapping_iri == MAPPING_IRI
        assert result[0].action is MappingAction.DELETE
        assert result[0].message == (
            "Unexpected error while trying to delete the mapping for class/property 'onto:Book'. "
            "Original status code: 503\n"
            "Original message: service unavailable"
        )


class TestDealWithBadRequest:
    def test_no_v3_errors_returns_text_message(self):
        response = ResponseCodeAndText(status_code=400, text="plain error text")
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "plain error text"

    def test_no_v3_errors_keeps_mapping_iri_of_a_deletion(self):
        response = ResponseCodeAndText(status_code=400, text="plain error text")
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.DELETE, MAPPING_IRI)
        assert len(result) == 1
        assert result[0].mapping_iri == MAPPING_IRI
        assert result[0].action is MappingAction.DELETE

    def test_class_not_found(self):
        response = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="",
            v3_errors=[ApiV3ErrorDetails("class_not_found", "not found", {})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "The class 'onto:Book' was not found in the ontology on the server."

    def test_property_not_found(self):
        response = ResponseCodeAndText(
            status_code=HTTPStatus.NOT_FOUND,
            text="",
            v3_errors=[ApiV3ErrorDetails("property_not_found", "not found", {})],
        )
        result = _get_detailed_user_message(PROP_IRI, response, MappingAction.ADD, None)
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
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri == "invalid-text"
        assert result[0].message == "The mapping IRI 'invalid-text' is not a valid external ontology IRI."

    def test_invalid_ontology_mapping_iri_prefers_the_iri_from_the_error(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("invalid_ontology_mapping_iri", "invalid", {"iri": "invalid-text"})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.DELETE, MAPPING_IRI)
        assert result[0].mapping_iri == "invalid-text"

    def test_unknown_error_code(self):
        response = ResponseCodeAndText(
            status_code=400,
            text="",
            v3_errors=[ApiV3ErrorDetails("some_unknown_code", "an unknown error", {})],
        )
        result = _get_detailed_user_message(CLASS_IRI, response, MappingAction.ADD, None)
        assert len(result) == 1
        assert result[0].prefixed_iri == PREFIXED_CLS
        assert result[0].mapping_iri is None
        assert result[0].message == "an unknown error"


class TestCommunicatePlannedDeletions:
    def test_nothing_to_delete(self, capsys: pytest.CaptureFixture[str]):
        _communicate_planned_deletions(MappingDeletions(classes=[], properties=[]))
        assert "No existing external mappings to delete." in capsys.readouterr().out

    def test_affected_entities_are_listed(self, capsys: pytest.CaptureFixture[str]):
        deletions = MappingDeletions(
            classes=[
                MappingDeletion(entity_iri=CLASS_IRI, mapping_iri=MAPPING_IRI),
                MappingDeletion(entity_iri=CLASS_IRI, mapping_iri="http://purl.org/ontology/bibo/Book"),
            ],
            properties=[MappingDeletion(entity_iri=PROP_IRI, mapping_iri=MAPPING_IRI)],
        )
        _communicate_planned_deletions(deletions)
        out = capsys.readouterr().out
        assert "3 existing external mapping(s) of 2 class(es)/property(ies) will be deleted." in out
        assert PREFIXED_CLS in out
        assert PREFIXED_PROP in out


class TestCommunicateUploadFailures:
    def test_report_contents(self, capsys: pytest.CaptureFixture[str]):
        failures = [
            MappingUploadFailure(
                prefixed_iri=PREFIXED_PROP, mapping_iri=None, message="add went wrong", action=MappingAction.ADD
            ),
            MappingUploadFailure(
                prefixed_iri=PREFIXED_CLS,
                mapping_iri=MAPPING_IRI,
                message="delete went wrong",
                action=MappingAction.DELETE,
            ),
        ]
        _communicate_upload_failures(failures)
        out = capsys.readouterr().out
        assert "2 mapping operation(s) failed." in out
        assert f"{PREFIXED_CLS} | Could not delete mapping '{MAPPING_IRI}' | Problem: delete went wrong" in out
        assert f"{PREFIXED_PROP} | Could not add mapping | Problem: add went wrong" in out
        assert RERUN_ADVICE in out

    def test_failures_are_sorted_by_entity(self, capsys: pytest.CaptureFixture[str]):
        failures = [
            MappingUploadFailure(
                prefixed_iri=PREFIXED_PROP, mapping_iri=None, message="second", action=MappingAction.ADD
            ),
            MappingUploadFailure(
                prefixed_iri=PREFIXED_CLS, mapping_iri=None, message="first", action=MappingAction.ADD
            ),
        ]
        _communicate_upload_failures(failures)
        out = capsys.readouterr().out
        assert out.index(PREFIXED_CLS) < out.index(PREFIXED_PROP)
