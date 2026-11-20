from http import HTTPStatus
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from rdflib import URIRef

from dsp_tools.commands.create.create_on_server.properties import _create_one_property
from dsp_tools.commands.create.create_on_server.properties import _get_property_create_order
from dsp_tools.commands.create.create_on_server.properties import _is_property_blocked
from dsp_tools.commands.create.create_on_server.properties import _make_graph_to_sort
from dsp_tools.commands.create.create_on_server.properties import create_all_properties
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import LAST_MOD_2
from test.unittests.commands.create.constants import LAST_MOD_3
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI
from test.unittests.commands.create.constants import PROJECT_IRI

KNORA_SUPER = "http://api.knora.org/ontology/knora-api/v2#hasValue"
EXTERNAL_SUPER = "http://xmlns.com/foaf/0.1/name"
FAILED_CLASS = "http://api.knora.org/ontology/0001/onto/v2#FailedClass"


def make_test_property(name: str, supers: list[str] | None = None) -> ParsedProperty:
    """Helper function to create a test property with standard defaults."""
    supr = supers if supers else []
    supr.append(KNORA_SUPER)
    return ParsedProperty(
        name=str(ONTO[name]),
        labels={"en": f"Label for {name}"},
        comments=None,
        supers=supr,
        object=KnoraObjectType.TEXT,
        subject=None,
        gui_element=GuiElement.SIMPLETEXT,
        node_name=None,
        onto_iri=str(ONTO_IRI),
    )


@pytest.fixture
def three_multiple_inheritance_props():
    """PropA inherits from both PropB and PropC (both independent)."""
    prop_b = make_test_property("PropB")
    prop_c = make_test_property("PropC")
    prop_a = make_test_property("PropA", supers=[prop_b.name, prop_c.name])
    return [prop_a, prop_b, prop_c]


@pytest.fixture
def three_independent_props():
    """PropA inherits from both PropB and PropC (both independent)."""
    prop_b = make_test_property("PropB")
    prop_c = make_test_property("PropC")
    prop_a = make_test_property("PropA")
    return [prop_a, prop_b, prop_c]


class TestGetPropertyOrder:
    def test_multiple_inheritance_scenario(self, three_multiple_inheritance_props):
        prop_a, _, _ = three_multiple_inheritance_props
        result = _get_property_create_order(three_multiple_inheritance_props)
        assert len(result) == 3
        assert result[-1] == prop_a.name

    def test_external_supers_do_not_break_sorting(self):
        p_b = make_test_property("PropB", supers=[])
        p_a = make_test_property("PropA", supers=[p_b.name, EXTERNAL_SUPER])
        result = _get_property_create_order([p_a, p_b])
        assert result == [p_b.name, p_a.name]
        assert KNORA_SUPER not in result


class TestMakeGraphToSort:
    def test_creates_graph_with_multiple_properties_no_internal_dependencies(self, three_independent_props):
        graph, node_to_iri = _make_graph_to_sort(three_independent_props)
        assert len(graph) == 3
        assert graph.num_edges() == 0  # No internal dependencies
        assert all(p.name in node_to_iri.values() for p in three_independent_props)

    def test_creates_graph_with_multiple_supers(self, three_multiple_inheritance_props):
        graph, _node_to_iri = _make_graph_to_sort(three_multiple_inheritance_props)
        assert len(graph) == 3
        assert graph.num_edges() == 2

    def test_creates_correct_node_to_iri_mapping(self, three_independent_props):
        _graph, node_to_iri = _make_graph_to_sort(three_independent_props)
        assert len(node_to_iri) == 3
        iris_in_mapping = set(node_to_iri.values())
        expected_iris = {p.name for p in three_independent_props}
        assert iris_in_mapping == expected_iris


class TestIsPropertyBlocked:
    def test_no_blocking_happy_path(self):
        prop = make_test_property("TestProp")
        created_iris = CreatedIriCollection()
        result = _is_property_blocked(prop, created_iris)
        assert result is None

    def test_super_property_failed(self):
        super_prop = make_test_property("SuperProp")
        prop = make_test_property("TestProp", supers=[super_prop.name])
        created_iris = CreatedIriCollection()
        created_iris.failed_properties.add(super_prop.name)
        result = _is_property_blocked(prop, created_iris)
        assert result is not None
        assert result.problem == UploadProblemType.PROPERTY_SUPER_FAILED
        assert result.problematic_object == prop.name

    def test_multiple_supers_some_failed(self):
        super_failed = make_test_property("SuperProp1")
        super_success = make_test_property("SuperProp2")
        prop = make_test_property("TestProp", supers=[super_failed.name, super_success.name])
        created_iris = CreatedIriCollection()
        created_iris.failed_properties.add(super_failed.name)
        created_iris.created_properties.add(super_success.name)
        result = _is_property_blocked(prop, created_iris)
        assert result is not None
        assert result.problem == UploadProblemType.PROPERTY_SUPER_FAILED

    def test_subject_class_failed(self):
        prop = make_test_property("TestProp")
        prop.subject = FAILED_CLASS
        created_iris = CreatedIriCollection()
        created_iris.failed_classes.add(FAILED_CLASS)
        result = _is_property_blocked(prop, created_iris)
        assert result is not None
        assert result.problem == UploadProblemType.PROPERTY_REFERENCES_FAILED_CLASS
        assert result.problematic_object == prop.name


class TestCreateOneProperty:
    @patch("dsp_tools.commands.create.create_on_server.properties.serialise_property_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.properties.should_retry_request")
    def test_success_on_first_attempt(self, mock_should_retry, mock_serialise):
        prop = make_test_property("TestProp")
        list_iri = None
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": URIRef(ONTO)},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        mock_client.post_new_property.return_value = LAST_MOD_2
        mock_serialise.return_value = {"@graph": []}
        result = _create_one_property(prop, list_iri, onto_lookup, mock_client)
        assert result == LAST_MOD_2
        mock_client.post_new_property.assert_called_once()
        mock_should_retry.assert_not_called()
        mock_client.get_last_modification_date.assert_not_called()

    @patch("dsp_tools.commands.create.create_on_server.properties.serialise_property_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.properties.should_retry_request")
    def test_success_after_retry(self, mock_should_retry, mock_serialise):
        prop = make_test_property("TestProp")
        list_iri = None
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        internal_error_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        mock_client.get_last_modification_date.return_value = LAST_MOD_2
        mock_client.post_new_property.side_effect = [internal_error_response, LAST_MOD_3]
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_property(prop, list_iri, onto_lookup, mock_client)
        assert result == LAST_MOD_3
        assert mock_client.post_new_property.call_count == 2
        mock_should_retry.assert_called_once_with(internal_error_response)
        mock_client.get_last_modification_date.assert_called_once_with(onto_lookup.project_iri, str(ONTO_IRI))
        assert mock_serialise.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.properties.serialise_property_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.properties.should_retry_request")
    def test_bad_request_failure(self, mock_should_retry, mock_serialise):
        prop = make_test_property("TestProp")
        list_iri = None
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        error_text = "Bad request: invalid property definition"
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text=error_text)
        mock_client.post_new_property.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = False
        result = _create_one_property(prop, list_iri, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == prop.name
        assert result.problem == error_text

    @patch("dsp_tools.commands.create.create_on_server.properties.serialise_property_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.properties.should_retry_request")
    def test_non_retryable_failure(self, mock_should_retry, mock_serialise):
        prop = make_test_property("TestProp")
        list_iri = None
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        response = ResponseCodeAndText(
            status_code=HTTPStatus.UNAVAILABLE_FOR_LEGAL_REASONS, text="A code that will not be retried"
        )
        mock_client.post_new_property.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = False
        result = _create_one_property(prop, list_iri, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == prop.name
        assert result.problem == UploadProblemType.PROPERTY_COULD_NOT_BE_CREATED

    @patch("dsp_tools.commands.create.create_on_server.properties.serialise_property_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.properties.should_retry_request")
    def test_retry_fails_again(self, mock_should_retry, mock_serialise):
        """Test that when retry is triggered but second attempt also fails, appropriate problem is returned."""
        prop = make_test_property("TestProp")
        list_iri = None
        onto_lookup = OntoLastModDateLookup(
            project_iri=PROJECT_IRI,
            onto_iris={"onto": ONTO_IRI},
            iri_to_last_modification_date={str(ONTO_IRI): LAST_MODIFICATION_DATE},
        )
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 1")
        second_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 2")
        mock_client.post_new_property.side_effect = [first_response, second_response]
        mock_client.get_last_modification_date.return_value = LAST_MOD_2
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_property(prop, list_iri, onto_lookup, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == prop.name
        assert result.problem == UploadProblemType.PROPERTY_COULD_NOT_BE_CREATED


class TestCreateAllProperties:
    @patch("dsp_tools.commands.create.create_on_server.properties.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.properties._get_property_create_order")
    @patch("dsp_tools.commands.create.create_on_server.properties._is_property_blocked")
    @patch("dsp_tools.commands.create.create_on_server.properties._create_one_property")
    def test_all_properties_succeed(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that all properties are created successfully."""
        prop1 = make_test_property("Prop1")
        prop2 = make_test_property("Prop2")
        properties = [prop1, prop2]
        mock_get_order.return_value = [prop1.name, prop2.name]
        mock_is_blocked.return_value = None
        mock_create_one.side_effect = [LAST_MOD_2, LAST_MOD_3]
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        list_lookup = ListNameToIriLookup(name2iri={})
        mock_client = MagicMock()
        result_iris, result_problems = create_all_properties(
            properties, project_iri_lookup, created_iris, list_lookup, mock_client
        )
        assert prop1.name in result_iris.created_properties
        assert prop2.name in result_iris.created_properties
        assert len(result_iris.failed_properties) == 0
        assert result_problems is None
        assert onto_lookup.update_last_mod_date.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.properties.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.properties._get_property_create_order")
    @patch("dsp_tools.commands.create.create_on_server.properties._is_property_blocked")
    @patch("dsp_tools.commands.create.create_on_server.properties._create_one_property")
    def test_property_blocked_by_super(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that a property blocked by failed super is skipped and added to problems."""
        prop1 = make_test_property("Prop1")
        properties = [prop1]
        mock_get_order.return_value = [prop1.name]
        blocking_problem = UploadProblem(prop1.name, UploadProblemType.PROPERTY_SUPER_FAILED)
        mock_is_blocked.return_value = blocking_problem
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        list_lookup = ListNameToIriLookup(name2iri={})
        mock_client = MagicMock()
        result_iris, result_problems = create_all_properties(
            properties, project_iri_lookup, created_iris, list_lookup, mock_client
        )
        assert prop1.name in result_iris.failed_properties
        assert prop1.name not in result_iris.created_properties
        mock_create_one.assert_not_called()
        assert result_problems is not None
        assert isinstance(result_problems, CollectedProblems)
        assert len(result_problems.problems) == 1

    @patch("dsp_tools.commands.create.create_on_server.properties.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.properties._get_property_create_order")
    @patch("dsp_tools.commands.create.create_on_server.properties._is_property_blocked")
    @patch("dsp_tools.commands.create.create_on_server.properties._create_one_property")
    def test_property_with_node_name(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that property with node_name calls list_lookup.get_iri."""
        prop1 = make_test_property("Prop1")
        prop1.node_name = "TestList"
        properties = [prop1]
        mock_get_order.return_value = [prop1.name]
        mock_is_blocked.return_value = None
        mock_create_one.return_value = LAST_MOD_2
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        list_lookup = MagicMock()
        list_iri = "http://rdfh.ch/lists/0001/testlist"
        list_lookup.get_iri.return_value = list_iri
        mock_client = MagicMock()
        result_iris, _ = create_all_properties(properties, project_iri_lookup, created_iris, list_lookup, mock_client)
        list_lookup.get_iri.assert_called_once_with("TestList")
        assert prop1.name in result_iris.created_properties

    @patch("dsp_tools.commands.create.create_on_server.properties.get_modification_date_onto_lookup")
    @patch("dsp_tools.commands.create.create_on_server.properties._get_property_create_order")
    @patch("dsp_tools.commands.create.create_on_server.properties._is_property_blocked")
    @patch("dsp_tools.commands.create.create_on_server.properties._create_one_property")
    def test_creation_fails(self, mock_create_one, mock_is_blocked, mock_get_order, mock_get_lookup):
        """Test that when creation fails, property is added to failed_properties and problems."""
        prop1 = make_test_property("Prop1")
        properties = [prop1]
        mock_get_order.return_value = [prop1.name]
        mock_is_blocked.return_value = None
        creation_problem = UploadProblem(prop1.name, UploadProblemType.PROPERTY_COULD_NOT_BE_CREATED)
        mock_create_one.return_value = creation_problem
        onto_lookup = MagicMock()
        mock_get_lookup.return_value = onto_lookup
        project_iri_lookup = ProjectIriLookup(project_iri=PROJECT_IRI)
        created_iris = CreatedIriCollection()
        list_lookup = ListNameToIriLookup(name2iri={})
        mock_client = MagicMock()
        result_iris, result_problems = create_all_properties(
            properties, project_iri_lookup, created_iris, list_lookup, mock_client
        )
        assert prop1.name in result_iris.failed_properties
        assert prop1.name not in result_iris.created_properties
        onto_lookup.update_last_mod_date.assert_not_called()
        assert result_problems is not None
        assert len(result_problems.problems) == 1
