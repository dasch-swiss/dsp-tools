# mypy: disable-error-code="no-untyped-def"
from unittest.mock import Mock

import pytest
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.create.create_on_server.cardinalities import _add_all_cardinalities_for_one_onto
from dsp_tools.commands.create.create_on_server.cardinalities import _add_cardinalities_for_one_class
from dsp_tools.commands.create.create_on_server.cardinalities import _add_one_cardinality
from dsp_tools.commands.create.create_on_server.cardinalities import _serialise_card
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from test.unittests.commands.create.constants import LAST_MODIFICATION_DATE
from test.unittests.commands.create.constants import ONTO
from test.unittests.commands.create.constants import ONTO_IRI

RESOURCE_IRI = ONTO.Resource
RES_1 = str(ONTO.Resource1)
RES_2 = str(ONTO.Resource2)
RES_3 = str(ONTO.Resource3)
PROP_IRI = ONTO.hasText

NEW_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", datatype=XSD.dateTimeStamp)


@pytest.fixture
def onto_client_ok() -> Mock:
    mock_client = Mock(spec=OntologyClient)
    new_mod_date = NEW_MODIFICATION_DATE
    mock_client.post_resource_cardinalities.return_value = new_mod_date
    return mock_client


@pytest.fixture
def created_iri_collection() -> CreatedIriCollection:
    return CreatedIriCollection(classes={str(RESOURCE_IRI), RES_1, RES_2, RES_3}, properties={str(PROP_IRI)})


class TestAddOneCardinality:
    def test_calls_client_and_returns_modification_date(self, onto_client_ok) -> None:
        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_date, problems = _add_one_cardinality(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok
        )
        assert result_date == NEW_MODIFICATION_DATE
        assert problems is None
        onto_client_ok.post_resource_cardinalities.assert_called_once()

    def test_returns_problem_when_client_returns_none(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.return_value = None

        property_card = ParsedPropertyCardinality(
            propname=str(PROP_IRI),
            cardinality=Cardinality.C_1,
            gui_order=None,
        )
        result_date, problem = _add_one_cardinality(
            property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client
        )
        assert result_date == LAST_MODIFICATION_DATE
        assert isinstance(problem, UploadProblem)
        assert problem.problem == ProblemType.CARDINALITY_COULD_NOT_BE_ADDED
        assert problem.problematic_object == "onto:Resource / onto:hasText"


class TestAddCardinalitiesForOneClass:
    def test_adds_single_cardinality_successfully(self, onto_client_ok) -> None:
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(
                    propname=str(PROP_IRI),
                    cardinality=Cardinality.C_1,
                    gui_order=None,
                )
            ],
        )
        successful_props = {str(PROP_IRI)}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok, successful_props
        )
        assert result_date == NEW_MODIFICATION_DATE
        assert len(problems) == 0
        assert onto_client_ok.post_resource_cardinalities.call_count == 1

    def test_adds_multiple_cardinalities_successfully(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z", datatype=XSD.dateTimeStamp),
            Literal("2025-10-14T14:01:00.000000Z", datatype=XSD.dateTimeStamp),
            Literal("2025-10-14T14:02:00.000000Z", datatype=XSD.dateTimeStamp),
        ]
        prop_1 = str(ONTO.hasText)
        prop_2 = str(ONTO.hasNumber)
        prop_3 = str(ONTO.hasDate)
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(propname=prop_1, cardinality=Cardinality.C_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_2, cardinality=Cardinality.C_0_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_3, cardinality=Cardinality.C_0_N, gui_order=None),
            ],
        )
        successful_props = {prop_1, prop_2, prop_3}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, successful_props
        )
        assert str(result_date) == "2025-10-14T14:02:00.000000Z"
        assert len(problems) == 0
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_skips_properties_not_in_successful_props(self, onto_client_ok) -> None:
        prop_1 = str(ONTO.hasText)
        prop_2 = str(ONTO.hasNumber)
        prop_3 = str(ONTO.hasDate)
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(propname=prop_1, cardinality=Cardinality.C_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_2, cardinality=Cardinality.C_0_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_3, cardinality=Cardinality.C_0_N, gui_order=None),
            ],
        )
        successful_props = {prop_1, prop_3}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok, successful_props
        )
        assert result_date == NEW_MODIFICATION_DATE
        assert len(problems) == 0
        assert onto_client_ok.post_resource_cardinalities.call_count == 2

    def test_handles_partial_failure(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        # Second call returns None (failure)
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z", datatype=XSD.dateTimeStamp),
            None,  # Failure
            Literal("2025-10-14T14:02:00.000000Z", datatype=XSD.dateTimeStamp),
        ]
        prop_1 = str(ONTO.hasText)
        prop_2 = str(ONTO.hasNumber)
        prop_3 = str(ONTO.hasDate)
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(propname=prop_1, cardinality=Cardinality.C_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_2, cardinality=Cardinality.C_0_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_3, cardinality=Cardinality.C_0_N, gui_order=None),
            ],
        )
        successful_props = {prop_1, prop_2, prop_3}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, successful_props
        )
        assert str(result_date) == "2025-10-14T14:02:00.000000Z"
        assert len(problems) == 1
        assert isinstance(problems[0], UploadProblem)
        assert problems[0].problem == ProblemType.CARDINALITY_COULD_NOT_BE_ADDED
        assert problems[0].problematic_object == "onto:Resource / onto:hasNumber"
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_handles_empty_cardinality_list(self, onto_client_ok) -> None:
        resource_card = ParsedClassCardinalities(class_iri=str(RESOURCE_IRI), cards=[])
        successful_props = {str(PROP_IRI)}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok, successful_props
        )
        assert result_date == LAST_MODIFICATION_DATE
        assert len(problems) == 0
        assert onto_client_ok.post_resource_cardinalities.call_count == 0

    def test_handles_all_properties_filtered_out(self, onto_client_ok) -> None:
        prop_1 = str(ONTO.hasText)
        prop_2 = str(ONTO.hasNumber)
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(propname=prop_1, cardinality=Cardinality.C_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_2, cardinality=Cardinality.C_0_1, gui_order=None),
            ],
        )
        successful_props = {str(ONTO.hasDate)}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok, successful_props
        )
        assert result_date == LAST_MODIFICATION_DATE
        assert len(problems) == 0
        assert onto_client_ok.post_resource_cardinalities.call_count == 0

    def test_updates_modification_date_sequentially(self) -> None:
        mock_client = Mock(spec=OntologyClient)
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z", datatype=XSD.dateTimeStamp),
            Literal("2025-10-14T14:01:00.000000Z", datatype=XSD.dateTimeStamp),
        ]
        prop_1 = str(ONTO.hasText)
        prop_2 = str(ONTO.hasNumber)
        resource_card = ParsedClassCardinalities(
            class_iri=str(RESOURCE_IRI),
            cards=[
                ParsedPropertyCardinality(propname=prop_1, cardinality=Cardinality.C_1, gui_order=None),
                ParsedPropertyCardinality(propname=prop_2, cardinality=Cardinality.C_0_1, gui_order=None),
            ],
        )
        successful_props = {prop_1, prop_2}
        result_date, problems = _add_cardinalities_for_one_class(
            resource_card, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, successful_props
        )
        assert str(result_date) == "2025-10-14T14:01:00.000000Z"
        assert len(problems) == 0


class TestAddAllCardinalities:
    def test_adds_single_cardinality_successfully(self, onto_client_ok, created_iri_collection) -> None:
        cardinalities = [
            ParsedClassCardinalities(
                class_iri=str(RESOURCE_IRI),
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            )
        ]
        result = _add_all_cardinalities_for_one_onto(
            cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, onto_client_ok, created_iri_collection
        )
        assert len(result) == 0
        assert onto_client_ok.post_resource_cardinalities.call_count == 1

    def test_adds_multiple_cardinalities_successfully(self, created_iri_collection) -> None:
        mock_client = Mock(spec=OntologyClient)
        # Return different modification dates for each call
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z", datatype=XSD.dateTimeStamp),
            Literal("2025-10-14T14:01:00.000000Z", datatype=XSD.dateTimeStamp),
            Literal("2025-10-14T14:02:00.000000Z", datatype=XSD.dateTimeStamp),
        ]
        cardinalities = [
            ParsedClassCardinalities(
                class_iri=RES_1,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=RES_2,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=RES_3,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_N,
                        gui_order=None,
                    )
                ],
            ),
        ]
        result = _add_all_cardinalities_for_one_onto(
            cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, created_iri_collection
        )
        assert len(result) == 0
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_handles_partial_failure(self, created_iri_collection) -> None:
        mock_client = Mock(spec=OntologyClient)
        # Second call returns None (failure)
        mock_client.post_resource_cardinalities.side_effect = [
            Literal("2025-10-14T14:00:00.000000Z", datatype=XSD.dateTimeStamp),
            None,  # Failure
            Literal("2025-10-14T14:02:00.000000Z", datatype=XSD.dateTimeStamp),
        ]
        cardinalities = [
            ParsedClassCardinalities(
                class_iri=RES_1,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=RES_2,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_1,
                        gui_order=None,
                    )
                ],
            ),
            ParsedClassCardinalities(
                class_iri=RES_3,
                cards=[
                    ParsedPropertyCardinality(
                        propname=str(PROP_IRI),
                        cardinality=Cardinality.C_0_N,
                        gui_order=None,
                    )
                ],
            ),
        ]
        result = _add_all_cardinalities_for_one_onto(
            cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, created_iri_collection
        )
        assert len(result) == 1
        assert mock_client.post_resource_cardinalities.call_count == 3

    def test_updates_modification_date_between_calls(self, created_iri_collection) -> None:
        mock_client = Mock(spec=OntologyClient)
        passed_graphs = []

        def capture_graph(graph: Graph) -> Literal:
            passed_graphs.append(graph)
            # Return a new modification date
            return Literal(f"2025-10-14T14:0{len(passed_graphs)}:00.000000Z")

        mock_client.post_resource_cardinalities.side_effect = capture_graph

        cardinalities = [
            ParsedClassCardinalities(
                class_iri=RES_1,
                cards=[ParsedPropertyCardinality(propname=str(PROP_IRI), cardinality=Cardinality.C_1, gui_order=None)],
            ),
            ParsedClassCardinalities(
                class_iri=RES_2,
                cards=[
                    ParsedPropertyCardinality(propname=str(PROP_IRI), cardinality=Cardinality.C_0_1, gui_order=None)
                ],
            ),
        ]
        result = _add_all_cardinalities_for_one_onto(
            cardinalities, ONTO_IRI, LAST_MODIFICATION_DATE, mock_client, created_iri_collection
        )
        assert len(result) == 0
        assert len(passed_graphs) == 2

        # First graph should have initial modification date
        first_graph_dates = passed_graphs[0]
        assert first_graph_dates["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        mod_date = next(iter(first_graph_dates["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"]))
        assert mod_date["@value"] == str(LAST_MODIFICATION_DATE)
        assert len(first_graph_dates["@graph"]) == 2

        # Second graph should have updated modification date from first response
        second_graph_dates = passed_graphs[1]
        assert second_graph_dates["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
        mod_date = next(iter(second_graph_dates["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"]))
        assert mod_date["@value"] == "2025-10-14T14:01:00.000000Z"
        assert len(second_graph_dates["@graph"]) == 2


def test_serialise_card():
    property_card = ParsedPropertyCardinality(
        propname=str(PROP_IRI),
        cardinality=Cardinality.C_1,
        gui_order=None,
    )
    serialised = _serialise_card(property_card, RESOURCE_IRI, ONTO_IRI, LAST_MODIFICATION_DATE)

    # Check ontology-level properties
    assert serialised["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2"
    assert serialised["@type"] == ["http://www.w3.org/2002/07/owl#Ontology"]
    assert serialised["http://api.knora.org/ontology/knora-api/v2#lastModificationDate"] == [
        {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": "2025-10-14T13:00:00.000000Z"}
    ]

    # Check graph contains exactly 2 nodes
    assert len(serialised["@graph"]) == 2

    # Find the resource and restriction nodes
    resource_node = next(
        n for n in serialised["@graph"] if n["@id"] == "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource"
    )
    restriction_nodes = [n for n in serialised["@graph"] if n["@id"].startswith("_:")]

    # Verify resource node structure
    assert resource_node["@type"] == ["http://www.w3.org/2002/07/owl#Class"]
    assert len(resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"]) == 1
    blank_node_id = resource_node["http://www.w3.org/2000/01/rdf-schema#subClassOf"][0]["@id"]
    assert blank_node_id.startswith("_:")

    # Verify restriction node structure
    assert len(restriction_nodes) == 1
    restriction_node = restriction_nodes[0]
    assert restriction_node["@id"] == blank_node_id
    assert restriction_node["@type"] == ["http://www.w3.org/2002/07/owl#Restriction"]
    assert restriction_node["http://www.w3.org/2002/07/owl#cardinality"] == [
        {"@type": "http://www.w3.org/2001/XMLSchema#integer", "@value": 1}
    ]
    assert restriction_node["http://www.w3.org/2002/07/owl#onProperty"] == [
        {"@id": "http://0.0.0.0:3333/ontology/9999/onto/v2#hasText"}
    ]
