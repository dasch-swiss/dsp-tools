import pytest
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExist
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatch
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ResourceValidationReportIdentifiers
from dsp_tools.commands.validate_data.models.validation import ResultWithDetail
from dsp_tools.commands.validate_data.models.validation import ResultWithoutDetail
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_with_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_without_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _reformat_one_with_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _reformat_one_without_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _separate_result_types
from test.unittests.commands.validate_data.constants import DASH
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


class TestSeparateResultTypes:
    def test_result_id_card_one(
        self, report_min_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = report_min_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_card_one")

    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = report_value_type_simpletext
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/id_simpletext")

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ResourceValidationReportIdentifiers]) -> None:
        res_g, onto_data_g, _ = report_value_type
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/id_uri")

    def test_result_geoname_not_number(
        self, report_regex: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = report_regex
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/geoname_not_number")

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = report_closed_constraint
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_closed_constraint")

    def test_result_id_max_card(
        self, report_max_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = report_max_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_max_card")


class TestQueryWithoutDetail:
    def test_result_id_card_one(
        self, report_min_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = report_min_card
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.MinCountConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testBoolean
        assert result.results_message == "1"
        assert not result.value

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = report_closed_constraint
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == DASH.ClosedByTypesConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testIntegerSimpleText
        assert (
            result.results_message
            == "Property onto:testIntegerSimpleText is not among those permitted for any of the types"
        )
        assert result.value == "http://data/value_id_closed_constraint"

    def test_result_id_max_card(
        self, report_max_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = report_max_card
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.MaxCountConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.results_message == "1"
        assert not result.value

    def test_result_empty_label(
        self, report_empty_label: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = report_empty_label
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.PatternConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == RDFS.label
        assert result.results_message == "The label must be a non-empty string"
        assert result.value == " "


class TestQueryWithDetail:
    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = report_value_type_simpletext
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testTextarea
        assert result.detail.results_message == "TextValue without formatting"
        assert result.detail.component == SH.MinCountConstraintComponent
        assert result.detail.value_type == KNORA_API.TextValue
        assert not result.detail.value

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ResourceValidationReportIdentifiers]) -> None:
        res, data, ids = report_value_type
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testUriValue
        assert result.detail.results_message == "UriValue"
        assert result.detail.component == SH.ClassConstraintComponent
        assert result.detail.value_type == KNORA_API.TextValue
        assert result.detail.value == "http://data/value_id_uri"

    def test_result_geoname_not_number(
        self, report_regex: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = report_regex
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.detail.results_message == "The value must be a valid geoname code"
        assert result.detail.component == SH.PatternConstraintComponent
        assert result.detail.value_type == KNORA_API.GeonameValue
        assert result.detail.value == "this-is-not-a-valid-code"

    def test_link_target_non_existent(
        self, report_link_target_non_existent: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = report_link_target_non_existent
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testHasLinkTo
        assert result.detail.results_message == "Resource"
        assert result.detail.component == SH.ClassConstraintComponent
        assert result.detail.value_type == KNORA_API.LinkValue
        assert result.detail.value == "http://data/other"

    def test_link_target_wrong_class(
        self, report_link_target_wrong_class: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = report_link_target_wrong_class
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.detail.results_message == "CardOneResource"
        assert result.detail.component == SH.ClassConstraintComponent
        assert result.detail.value_type == KNORA_API.LinkValue
        assert result.detail.value == "http://data/id_9_target"


class TestReformatWithoutDetail:
    def test_min(self, extracted_min_card: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(extracted_min_card)
        assert isinstance(result, MinCardinalityViolation)
        assert result.res_id == "id_card_one"
        assert result.res_type == "onto:ClassInheritedCardinalityOverwriting"
        assert result.prop_name == "onto:testBoolean"
        assert result.expected_cardinality == "1"

    def test_max(self, extracted_max_card: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(extracted_max_card)
        assert isinstance(result, MaxCardinalityViolation)
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected_cardinality == "0-1"

    def test_violation_empty_label(self, extracted_empty_label: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(extracted_empty_label)
        assert isinstance(result, ContentRegexViolation)
        assert result.res_id == "empty_label"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "rdfs:label"
        assert result.expected_format == "The label must be a non-empty string"
        assert not result.actual_content

    def test_closed(self, extracted_closed_constraint: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(extracted_closed_constraint)
        assert isinstance(result, NonExistentCardinalityViolation)
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"


class TestReformatWithDetail:
    def test_value_type_simpletext(self, extracted_value_type_simpletext: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_value_type_simpletext)
        assert isinstance(result, ValueTypeViolation)
        assert result.res_id == "id_simpletext"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testTextarea"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "TextValue without formatting"

    def test_value_type(self, extracted_value_type: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_value_type)
        assert isinstance(result, ValueTypeViolation)
        assert result.res_id == "id_uri"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testUriValue"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "UriValue"

    def test_violation_regex(self, extracted_regex: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_regex)
        assert isinstance(result, ContentRegexViolation)
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_format == "The value must be a valid geoname code"
        assert result.actual_content == "this-is-not-a-valid-code"

    def test_unknown(self, extracted_unknown_component: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_unknown_component)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)

    def test_link_target_non_existent(self, extracted_link_target_non_existent: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_link_target_non_existent)
        assert isinstance(result, LinkedResourceDoesNotExist)
        assert result.res_id == "link_target_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.link_target_id == "other"

    def test_link_target_wrong_class(self, extracted_link_target_wrong_class: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(extracted_link_target_wrong_class)
        assert isinstance(result, LinkTargetTypeMismatch)
        assert result.res_id == "link_target_wrong_class"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkToCardOneResource"
        assert result.link_target_id == "id_9_target"
        assert result.expected_type == "CardOneResource"


if __name__ == "__main__":
    pytest.main([__file__])
