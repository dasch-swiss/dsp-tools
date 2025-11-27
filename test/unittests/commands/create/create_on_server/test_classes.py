# mypy: disable-error-code="no-untyped-def"

from http import HTTPStatus
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from rdflib import URIRef

from dsp_tools.commands.create.create_on_server.classes import _create_one_class
from dsp_tools.commands.create.create_on_server.classes import _get_class_create_order
from dsp_tools.commands.create.create_on_server.classes import _is_class_blocked
from dsp_tools.commands.create.create_on_server.classes import _make_graph_to_sort
from dsp_tools.commands.create.create_on_server.classes import create_all_classes
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import LAST_MOD_2
from test.unittests.commands.create.constants import LAST_MOD_3
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI
from test.unittests.commands.create.constants import PROJECT_IRI

KNORA_SUPER = "http://api.knora.org/ontology/knora-api/v2#Resource"
EXTERNAL_SUPER = "http://xmlns.com/foaf/0.1/Person"
FAILED_CLASS = "http://api.knora.org/ontology/0001/onto/v2#FailedClass"


def make_test_class(name: str, supers: list[str] | None = None) -> ParsedClass:
    """Helper function to create a test class with standard defaults."""
    supr = supers if supers else []
    supr.append(KNORA_SUPER)
    return ParsedClass(
        name=str(ONTO[name]),
        labels={"en": f"Label for {name}"},
        comments=None,
        supers=supr,
        onto_iri=str(ONTO_IRI),
    )


@pytest.fixture
def three_multiple_inheritance_classes():
    """ClassA inherits from both ClassB and ClassC (both independent)."""
    class_b = make_test_class("ClassB")
    class_c = make_test_class("ClassC")
    class_a = make_test_class("ClassA", supers=[class_b.name, class_c.name])
    return [class_a, class_b, class_c]


@pytest.fixture
def three_independent_classes():
    """Three classes with no internal dependencies."""
    class_a = make_test_class("ClassA")
    class_b = make_test_class("ClassB")
    class_c = make_test_class("ClassC")
    return [class_a, class_b, class_c]


class TestGetClassOrder:
    def test_multiple_inheritance_scenario(self, three_multiple_inheritance_classes):
        class_a, _, _ = three_multiple_inheritance_classes
        result = _get_class_create_order(three_multiple_inheritance_classes)
        assert len(result) == 3
        assert result[-1] == class_a.name

    def test_external_supers_do_not_break_sorting(self):
        c_b = make_test_class("ClassB", supers=[])
        c_a = make_test_class("ClassA", supers=[c_b.name, EXTERNAL_SUPER])
        result = _get_class_create_order([c_a, c_b])
        assert result == [c_b.name, c_a.name]
        assert KNORA_SUPER not in result


class TestMakeGraphToSort:
    def test_creates_graph_with_multiple_classes_no_internal_dependencies(self, three_independent_classes):
        graph, node_to_iri = _make_graph_to_sort(three_independent_classes)
        assert len(graph) == 3
        assert graph.num_edges() == 0  # No internal dependencies
        assert all(c.name in node_to_iri.values() for c in three_independent_classes)

    def test_creates_graph_with_multiple_supers(self, three_multiple_inheritance_classes):
        graph, _node_to_iri = _make_graph_to_sort(three_multiple_inheritance_classes)
        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_correct_node_to_iri_mapping(self, three_independent_classes):
        _graph, node_to_iri = _make_graph_to_sort(three_independent_classes)
        assert len(node_to_iri) == 3
        iris_in_mapping = set(node_to_iri.values())
        expected_iris = {c.name for c in three_independent_classes}
        assert iris_in_mapping == expected_iris


class TestIsClassBlocked:
    def test_no_blocking_happy_path(self):
        cls = make_test_class("TestClass")
        created_iris = CreatedIriCollection()
        result = _is_class_blocked(cls.name, set(cls.supers), created_iris)
        assert result is None

    def test_super_class_failed(self):
        super_cls = make_test_class("SuperClass")
        cls = make_test_class("TestClass", supers=[super_cls.name])
        created_iris = CreatedIriCollection()
        created_iris.failed_classes.add(super_cls.name)
        result = _is_class_blocked(cls.name, set(cls.supers), created_iris)
        assert result is not None
        assert result.problem == UploadProblemType.CLASS_SUPER_FAILED
        assert result.problematic_object == cls.name

    def test_multiple_supers_some_failed(self):
        super_failed = make_test_class("SuperClass1")
        super_success = make_test_class("SuperClass2")
        cls = make_test_class("TestClass", supers=[super_failed.name, super_success.name])
        created_iris = CreatedIriCollection()
        created_iris.failed_classes.add(super_failed.name)
        created_iris.created_classes.add(super_success.name)
        result = _is_class_blocked(cls.name, set(cls.supers), created_iris)
        assert result is not None
        assert result.problem == UploadProblemType.CLASS_SUPER_FAILED


class TestCreateOneClass:
    @patch("dsp_tools.commands.create.create_on_server.classes.serialise_class_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.classes.should_retry_request")
    def test_success_on_first_attempt(self, mock_should_retry, mock_serialise):
        cls = make_test_class("TestClass")
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": URIRef(ONTO)},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        mock_client.post_new_class.return_value = LAST_MOD_2
        mock_serialise.return_value = {"@graph": []}
        result = _create_one_class(cls, onto_lookup, mock_client)
        assert result == LAST_MOD_2
        mock_client.post_new_class.assert_called_once()
        mock_should_retry.assert_not_called()
        mock_client.get_last_modification_date.assert_not_called()

    @patch("dsp_tools.commands.create.create_on_server.classes.serialise_class_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.classes.should_retry_request")
    def test_success_after_retry(self, mock_should_retry, mock_serialise):
        cls = make_test_class("TestClass")
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        internal_error_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        mock_client.get_last_modification_date.return_value = LAST_MOD_2
        mock_client.post_new_class.side_effect = [internal_error_response, LAST_MOD_3]
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_class(cls, onto_lookup, mock_client)
        assert result == LAST_MOD_3
        assert mock_client.post_new_class.call_count == 2
        mock_should_retry.assert_called_once_with(internal_error_response)
        mock_client.get_last_modification_date.assert_called_once_with(onto_lookup.project_iri, str(ONTO_IRI))
        assert mock_serialise.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.classes.serialise_class_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.classes.should_retry_request")
    def test_bad_request_failure(self, mock_should_retry, mock_serialise):
        cls = make_test_class("TestClass")
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        error_text = "Bad request: invalid class definition"
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text=error_text)
        mock_client.post_new_class.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = False
        result = _create_one_class(cls, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == cls.name
        assert result.problem == error_text

    @patch("dsp_tools.commands.create.create_on_server.classes.serialise_class_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.classes.should_retry_request")
    def test_non_retryable_failure(self, mock_should_retry, mock_serialise):
        cls = make_test_class("TestClass")
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        response = ResponseCodeAndText(
            status_code=HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS, text="A code that will not be retried"
        )
        mock_client.post_new_class.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = False
        result = _create_one_class(cls, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == cls.name
        assert result.problem == UploadProblemType.CLASS_COULD_NOT_BE_CREATED

    @patch("dsp_tools.commands.create.create_on_server.classes.serialise_class_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.classes.should_retry_request")
    def test_retry_fails_again(self, mock_should_retry, mock_serialise):
        """Test that when retry is triggered but second attempt also fails, appropriate problem is returned."""
        cls = make_test_class("TestClass")
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 1")
        second_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 2")
        mock_client.post_new_class.side_effect = [first_response, second_response]
        mock_client.get_last_modification_date.return_value = LAST_MOD_2
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_class(cls, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == cls.name
        assert result.problem == UploadProblemType.CLASS_COULD_NOT_BE_CREATED


class TestCreateAllClasses:
    @patch("dsp_tools.commands.create.create_on_server.classes.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.classes._get_class_create_order")
    @patch("dsp_tools.commands.create.create_on_server.classes._is_class_blocked")
    @patch("dsp_tools.commands.create.create_on_server.classes._create_one_class")
    def test_all_classes_succeed(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that all classes are created successfully."""
        class1 = make_test_class("Class1")
        class2 = make_test_class("Class2")
        classes = [class1, class2]
        mock_get_order.return_value = [class1.name, class2.name]
        mock_is_blocked.return_value = None
        mock_create_one.side_effect = [LAST_MOD_2, LAST_MOD_3]
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        mock_client = MagicMock()
        result_iris, result_problems = create_all_classes(classes, project_iri_lookup, created_iris, mock_client)
        assert class1.name in result_iris.created_classes
        assert class2.name in result_iris.created_classes
        assert len(result_iris.failed_classes) == 0
        assert result_problems is None
        assert onto_lookup.update_last_mod_date.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.classes.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.classes._get_class_create_order")
    @patch("dsp_tools.commands.create.create_on_server.classes._is_class_blocked")
    @patch("dsp_tools.commands.create.create_on_server.classes._create_one_class")
    def test_class_blocked_by_super(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that a class blocked by failed super is skipped and added to problems."""
        class1 = make_test_class("Class1")
        classes = [class1]
        mock_get_order.return_value = [class1.name]
        blocking_problem = UploadProblem(class1.name, UploadProblemType.CLASS_SUPER_FAILED)
        mock_is_blocked.return_value = blocking_problem
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        mock_client = MagicMock()
        result_iris, result_problems = create_all_classes(classes, project_iri_lookup, created_iris, mock_client)
        assert class1.name in result_iris.failed_classes
        assert class1.name not in result_iris.created_classes
        mock_create_one.assert_not_called()
        assert result_problems is not None
        assert isinstance(result_problems, CollectedProblems)
        assert len(result_problems.problems) == 1

    @patch("dsp_tools.commands.create.create_on_server.classes.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.classes._get_class_create_order")
    @patch("dsp_tools.commands.create.create_on_server.classes._is_class_blocked")
    @patch("dsp_tools.commands.create.create_on_server.classes._create_one_class")
    def test_creation_fails(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that when creation fails, class is added to failed_classes and problems."""
        class1 = make_test_class("Class1")
        classes = [class1]
        mock_get_order.return_value = [class1.name]
        mock_is_blocked.return_value = None
        creation_problem = UploadProblem(class1.name, UploadProblemType.CLASS_COULD_NOT_BE_CREATED)
        mock_create_one.return_value = creation_problem
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        mock_client = MagicMock()
        result_iris, result_problems = create_all_classes(classes, project_iri_lookup, created_iris, mock_client)
        assert class1.name in result_iris.failed_classes
        assert class1.name not in result_iris.created_classes
        onto_lookup.update_last_mod_date.assert_not_called()
        assert result_problems is not None
        assert len(result_problems.problems) == 1
