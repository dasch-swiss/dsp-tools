from pathlib import Path
from typing import Iterator

import pytest
from rdflib import BNode
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.input_problems import DuplicateValueProblem
from dsp_tools.commands.validate_data.models.input_problems import FileValueNotAllowedProblem
from dsp_tools.commands.validate_data.models.input_problems import FileValueProblem
from dsp_tools.commands.validate_data.models.input_problems import GenericProblemWithInput
from dsp_tools.commands.validate_data.models.input_problems import GenericProblemWithMessage
from dsp_tools.commands.validate_data.models.input_problems import InputRegexProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExistProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatchProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeProblem
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.reformat_validaton_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from dsp_tools.commands.validate_data.validate_ontology import validate_ontology
from test.e2e_validate_data.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
LOCAL_API = "http://0.0.0.0:3333"


@pytest.fixture(scope="module")
def _create_projects() -> Iterator[None]:
    with get_containers():
        assert create_project(Path("testdata/validate-data/generic/project.json"), CREDS)
        assert create_project(Path("testdata/validate-data/special_characters/project_special_characters.json"), CREDS)
        assert create_project(Path("testdata/validate-data/inheritance/project_inheritance.json"), CREDS)
        assert create_project(Path("testdata/validate-data/erroneous_ontology/project_erroneous_ontology.json"), CREDS)
        assert create_project(Path("testdata/json-project/test-project-systematic.json"), CREDS)
        yield


@pytest.fixture(scope="module")
def api_con() -> ApiConnection:
    return ApiConnection(LOCAL_API)


@pytest.fixture(scope="module")
def shacl_validator(api_con: ApiConnection) -> ShaclValidator:
    return ShaclValidator(api_con)


@pytest.fixture(scope="module")
def unknown_classes_graphs(_create_projects: Iterator[None], api_con: ApiConnection) -> RDFGraphs:
    file = Path("testdata/validate-data/generic/unknown_classes.xml")
    return _get_parsed_graphs(api_con, file)


@pytest.fixture(scope="module")
def cardinality_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/cardinality_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def content_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/content_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def every_combination_once(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/every_combination_once.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def value_type_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/value_type_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def unique_value_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/unique_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def file_value_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/file_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def dsp_inbuilt_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def special_characters_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/special_characters/special_characters_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def inheritance_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/inheritance/inheritance_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def validate_ontology_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> OntologyValidationProblem | None:
    file = Path("testdata/validate-data/erroneous_ontology/erroneous_ontology.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return validate_ontology(graphs.ontos, shacl_validator, None)


def test_extract_identifiers_of_resource_results(every_combination_once: ValidationReportGraphs) -> None:
    report_and_onto = every_combination_once.validation_graph + every_combination_once.onto_graph
    data_and_onto = every_combination_once.data_graph + every_combination_once.onto_graph
    result = _extract_base_info_of_resource_results(report_and_onto, data_and_onto)
    result_sorted = sorted(result, key=lambda x: str(x.resource_iri))
    expected_iris = [
        (URIRef("http://data/empty_label"), None),
        (URIRef("http://data/geoname_not_number"), BNode),
        (URIRef("http://data/id_card_one"), None),
        (URIRef("http://data/id_closed_constraint"), None),
        (URIRef("http://data/id_max_card"), None),
        (URIRef("http://data/id_missing_file_value"), None),
        (URIRef("http://data/id_simpletext"), BNode),
        (URIRef("http://data/id_uri"), BNode),
        (URIRef("http://data/identical_values"), None),
        (URIRef("http://data/link_target_non_existent"), BNode),
        (URIRef("http://data/link_target_wrong_class"), BNode),
        (URIRef("http://data/list_node_non_existent"), BNode),
        (URIRef("http://data/missing_seqnum"), None),
        (URIRef("http://data/video_segment_start_larger_than_end"), BNode),
        (URIRef("http://data/video_segment_wrong_bounds"), BNode),
        (URIRef("http://data/video_segment_wrong_bounds"), BNode),
    ]
    assert len(result) == len(expected_iris)
    for result_info, expected_iri in zip(result_sorted, expected_iris):
        assert result_info.resource_iri == expected_iri[0]
        if expected_iri[1] is None:
            assert not result_info.detail
        else:
            detail_base_info = result_info.detail
            assert isinstance(detail_base_info, DetailBaseInfo)
            assert isinstance(detail_base_info.detail_bn, expected_iri[1])


class TestCheckConforms:
    @pytest.mark.usefixtures("_create_projects")
    def test_cardinality_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/cardinality_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        cardinality_correct = _get_validation_result(graphs, shacl_validator, None)
        assert cardinality_correct.conforms

    def test_cardinality_violation(self, cardinality_violation: ValidationReportGraphs) -> None:
        assert not cardinality_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_content_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/content_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        content_correct = _get_validation_result(graphs, shacl_validator, None)
        assert content_correct.conforms

    def test_content_violation(self, content_violation: ValidationReportGraphs) -> None:
        assert not content_violation.conforms

    def test_every_combination_once(self, every_combination_once: ValidationReportGraphs) -> None:
        assert not every_combination_once.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_minimal_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/minimal_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        minimal_correct = _get_validation_result(graphs, shacl_validator, None)
        assert minimal_correct.conforms

    def test_value_type_violation(self, value_type_violation: ValidationReportGraphs) -> None:
        assert not value_type_violation.conforms

    def test_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        assert not unique_value_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_file_value_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/file_value_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        file_value_correct = _get_validation_result(graphs, shacl_validator, None)
        assert file_value_correct.conforms

    def test_file_value_cardinality_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        assert not file_value_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_dsp_inbuilt_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, None)
        assert dsp_inbuilt_correct.conforms

    def test_dsp_inbuilt_violation(self, dsp_inbuilt_violation: ValidationReportGraphs) -> None:
        assert not dsp_inbuilt_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_special_characters_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/special_characters/special_characters_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        special_characters_correct = _get_validation_result(graphs, shacl_validator, None)
        assert special_characters_correct.conforms

    def test_special_characters_violation(self, special_characters_violation: ValidationReportGraphs) -> None:
        assert not special_characters_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_inheritance_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/inheritance/inheritance_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        inheritance_correct = _get_validation_result(graphs, shacl_validator, None)
        assert inheritance_correct.conforms

    def test_inheritance_violation(self, inheritance_violation: ValidationReportGraphs) -> None:
        assert not inheritance_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_systematic_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/xml-data/test-data-systematic.xml")
        graphs = _get_parsed_graphs(api_con, file)
        systematic_correct = _get_validation_result(graphs, shacl_validator, None)
        assert systematic_correct.conforms


class TestReformatValidationGraph:
    def test_reformat_cardinality_violation(self, cardinality_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(cardinality_violation)
        expected_info_tuples = [
            (MinCardinalityProblem, "id_card_one"),
            (NonExistentCardinalityProblem, "id_closed_constraint"),
            (MaxCardinalityProblem, "id_max_card"),
            (MinCardinalityProblem, "id_min_card"),
            (NonExistentCardinalityProblem, "super_prop_no_card"),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, expected_info[0])
            assert one_result.res_id == expected_info[1]

    def test_reformat_value_type_violation(self, value_type_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(value_type_violation)
        assert not result.unexpected_results
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        expected_info_tuples = [
            ("id_bool", "BooleanValue", "onto:testBoolean"),
            ("id_color", "ColorValue", "onto:testColor"),
            ("id_date", "DateValue", "onto:testSubDate1"),
            ("id_decimal", "DecimalValue", "onto:testDecimalSimpleText"),
            ("id_geoname", "GeonameValue", "onto:testGeoname"),
            ("id_integer", "IntValue", "onto:testIntegerSimpleText"),
            ("id_link", "LinkValue", "onto:testHasLinkTo"),
            ("id_list", "ListValue", "onto:testListProp"),
            ("id_richtext", "TextValue with formatting", "onto:testRichtext"),
            ("id_simpletext", "TextValue without formatting", "onto:testTextarea"),
            ("id_time", "TimeValue", "onto:testTimeValue"),
            ("id_uri", "UriValue", "onto:testUriValue"),
            ("is_link_should_be_integer", "IntValue", "onto:testIntegerSpinbox"),
            ("is_link_should_be_text", "TextValue without formatting", "onto:testTextarea"),
        ]
        assert len(result.problems) == len(expected_info_tuples)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, ValueTypeProblem)
            assert one_result.res_id == expected_info[0]
            assert one_result.expected_type == expected_info[1]
            assert one_result.prop_name == expected_info[2]

    def test_reformat_content_violation(self, content_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(content_violation)
        assert not result.unexpected_results
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        expected_info_tuples = [
            (
                "comment_on_value_empty",
                "onto:testUriValue",
                "The comment on the value must be a non-empty string",
            ),
            (
                "comment_on_value_whitespace",
                "onto:testUriValue",
                "The comment on the value must be a non-empty string",
            ),
            ("empty_label", "rdfs:label", "The label must be a non-empty string"),
            ("empty_text_rich", "onto:testRichtext", "The value must be a non-empty string"),
            ("empty_text_simple", "onto:testTextarea", "The value must be a non-empty string"),
            ("geoname_not_number", "onto:testGeoname", "The value must be a valid geoname code"),
            ("link_target_non_existent", "onto:testHasLinkTo", "other"),
            ("link_target_wrong_class", "onto:testHasLinkToCardOneResource", "id_9_target"),
            (
                "list_name_attrib_empty",
                "onto:testListProp",
                (
                    "A valid node from the list 'firstList' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
            ),
            (
                "list_name_non_existent",
                "onto:testListProp",
                (
                    "A valid node from the list 'firstList' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
            ),
            (
                "list_node_non_existent",
                "onto:testListProp",
                (
                    "A valid node from the list 'firstList' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
            ),
            ("text_only_whitespace_simple", "onto:testTextarea", "The value must be a non-empty string"),
        ]
        assert len(result.problems) == len(expected_info_tuples)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.res_id == expected_info[0]
            assert one_result.prop_name == expected_info[1]
            if isinstance(one_result, InputRegexProblem):
                assert one_result.expected_format == expected_info[2]
            elif isinstance(one_result, GenericProblemWithInput):
                assert one_result.results_message == expected_info[2]
            elif isinstance(one_result, LinkTargetTypeMismatchProblem):
                assert one_result.link_target_id == expected_info[2]
            elif isinstance(one_result, LinkedResourceDoesNotExistProblem):
                assert one_result.link_target_id == expected_info[2]
            else:
                assert isinstance(one_result, LinkedResourceDoesNotExistProblem)

    def test_reformat_every_constraint_once(self, every_combination_once: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(every_combination_once)
        expected_info_tuples = [
            ("empty_label", InputRegexProblem),
            ("geoname_not_number", InputRegexProblem),
            ("id_card_one", MinCardinalityProblem),
            ("id_closed_constraint", NonExistentCardinalityProblem),
            ("id_max_card", MaxCardinalityProblem),
            ("id_missing_file_value", FileValueProblem),
            ("id_simpletext", ValueTypeProblem),
            ("id_uri", ValueTypeProblem),
            ("identical_values", DuplicateValueProblem),
            ("link_target_non_existent", LinkedResourceDoesNotExistProblem),
            ("link_target_wrong_class", LinkTargetTypeMismatchProblem),
            ("list_node_non_existent", GenericProblemWithInput),
            ("missing_seqnum", GenericProblemWithMessage),
            ("video_segment_start_larger_than_end", GenericProblemWithInput),
            ("video_segment_wrong_bounds", GenericProblemWithInput),  # once for start that is less than zero
            ("video_segment_wrong_bounds", GenericProblemWithInput),  # once for the end that is zero
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.res_id == expected_info[0]
            assert isinstance(one_result, expected_info[1])

    def test_reformat_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(unique_value_violation)
        expected_ids = [
            "identical_values_LinkValue",
            "identical_values_listNode",
            "identical_values_valueAsString",
            "identical_values_valueHas",
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_ids)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_id in zip(sorted_problems, expected_ids):
            assert isinstance(one_result, DuplicateValueProblem)
            assert one_result.res_id == expected_id

    def test_reformat_file_value_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(file_value_violation)
        expected_info_tuples = [
            ("id_archive_missing", FileValueProblem),
            ("id_archive_unknown", FileValueProblem),
            ("id_audio_missing", FileValueProblem),
            ("id_audio_unknown", FileValueProblem),
            ("id_document_missing", FileValueProblem),
            ("id_document_unknown", FileValueProblem),
            ("id_resource_without_representation", FileValueNotAllowedProblem),
            ("id_still_image_missing", FileValueProblem),
            ("id_still_image_unknown", FileValueProblem),
            ("id_text_missing", FileValueProblem),
            ("id_text_unknown", FileValueProblem),
            ("id_video_missing", FileValueProblem),
            ("id_video_unknown", FileValueProblem),
            ("id_wrong_file_type", FileValueProblem),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, expected_info[1])
            assert one_result.res_id == expected_info[0]

    def test_reformat_dsp_inbuilt_violation(self, dsp_inbuilt_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(dsp_inbuilt_violation)
        expected_info_tuples = [
            ("audio_segment_target_is_video", LinkTargetTypeMismatchProblem),
            ("audio_segment_target_non_existent", LinkedResourceDoesNotExistProblem),
            ("link_obj_target_non_existent", LinkedResourceDoesNotExistProblem),
            ("missing_isPartOf", GenericProblemWithMessage),
            ("missing_seqnum", GenericProblemWithMessage),
            ("region_invalid_geometry", InputRegexProblem),
            ("region_isRegionOf_resource_does_not_exist", LinkedResourceDoesNotExistProblem),
            ("region_isRegionOf_resource_not_a_representation", LinkTargetTypeMismatchProblem),
            ("target_must_be_a_representation", LinkTargetTypeMismatchProblem),
            ("target_must_be_an_image_representation", LinkTargetTypeMismatchProblem),
            ("video_segment_start_larger_than_end", GenericProblemWithInput),
            ("video_segment_target_is_audio", LinkTargetTypeMismatchProblem),
            ("video_segment_target_non_existent", LinkedResourceDoesNotExistProblem),
            ("video_segment_wrong_bounds", GenericProblemWithInput),  # once for start that is less than zero
            ("video_segment_wrong_bounds", GenericProblemWithInput),  # once for the end that is zero
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert isinstance(one_result, expected_info[1])
            assert one_result.res_id == expected_info[0]

    def test_reformat_special_characters_violation(self, special_characters_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(special_characters_violation)
        expected_tuples = [
            (
                "node_backslash",
                (
                    "A valid node from the list 'list \\ ' space' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
                "list \\ ' space / other \\ backslash",
            ),
            (
                "node_double_quote",
                (
                    "A valid node from the list 'list \\ ' space' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
                '''list \\ ' space / other double quote "''',
            ),
            (
                "node_single_quote",
                (
                    "A valid node from the list 'list \\ ' space' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
                "list \\ ' space / other single quote '",
            ),
            ("non_ascii_latin_alphabet", "", ""),
            ("non_ascii_other_alphabet", "", ""),
            ("special_char", "", ""),
            (
                "wrong_list_name",
                (
                    "A valid node from the list 'list \\ ' space' must be used with this property "
                    "(input displayed in format 'listName / NodeName')."
                ),
                "other /  \\ backslash",
            ),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for prblm, expected in zip(sorted_problems, expected_tuples):
            if isinstance(prblm, GenericProblemWithInput):
                assert prblm.res_id == expected[0]
                assert prblm.problem == expected[1]
                assert prblm.actual_input == expected[2]
            elif isinstance(prblm, InputRegexProblem):
                assert prblm.res_id == expected[0]

    def test_reformat_inheritance_violation(self, inheritance_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(inheritance_violation)
        expected_results = [
            ("ResourceSubCls1", {"onto:hasText0"}),
            ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
            ("ResourceSubCls2", {"onto:hasTextSubProp1", "onto:hasText0"}),
            ("ResourceUnrelated", {"onto:hasText0"}),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_results)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected in zip(sorted_problems, expected_results):
            assert isinstance(one_result, NonExistentCardinalityProblem)
            assert one_result.res_id == expected[0]
            assert one_result.prop_name in expected[1]

    def test_validate_ontology_violation(self, validate_ontology_violation: ValidationReportGraphs | None) -> None:
        assert isinstance(validate_ontology_violation, OntologyValidationProblem)
        erroneous_cards_msg = {
            "isPartOf must either have cardinality 1 or 0-1.",
            "seqnum must either have cardinality 1 or 0-1.",
        }
        missing_is_part_of = {"A class with a cardinality for seqnum also requires a cardinality for isPartOf."}
        missing_seqnum = {"A class with a cardinality for isPartOf also requires a cardinality for seqnum."}
        mixed_cards = {"The cardinalities for seqnum and isPartOf must be identical within one resource class."}
        expected_results = [
            ("error:ImageWithKnoraProp_ErroneousCards", erroneous_cards_msg),
            ("error:ImageWithKnoraProp_ErroneousCards", erroneous_cards_msg),
            ("error:ImageWithKnoraProp_MissingIsPartOf", missing_is_part_of),
            ("error:ImageWithKnoraProp_MissingSeqnum", missing_seqnum),
            ("error:ImageWithKnoraProp_MixedValidCards", mixed_cards),
            ("error:ImageWithSubProp_ErroneousCards", erroneous_cards_msg),
            ("error:ImageWithSubProp_ErroneousCards", erroneous_cards_msg),
            ("error:ImageWithSubProp_MissingIsPartOf", missing_is_part_of),
            ("error:ImageWithSubProp_MissingSeqnum", missing_seqnum),
            ("error:ImageWithSubProp_MixedValidCards", mixed_cards),
        ]
        sorted_problems = sorted(validate_ontology_violation.problems, key=lambda x: x.res_iri)
        assert len(validate_ontology_violation.problems) == len(expected_results)
        for one_result, expected in zip(sorted_problems, expected_results):
            assert one_result.res_iri == expected[0]
            assert one_result.msg in expected[1]


def test_check_for_unknown_resource_classes(unknown_classes_graphs: RDFGraphs) -> None:
    result = _check_for_unknown_resource_classes(unknown_classes_graphs)
    assert isinstance(result, UnknownClassesInData)
    expected = {"onto:NonExisting", "unknown:ClassWithEverything", "unknownClass"}
    assert result.unknown_classes == expected


if __name__ == "__main__":
    pytest.main([__file__])
