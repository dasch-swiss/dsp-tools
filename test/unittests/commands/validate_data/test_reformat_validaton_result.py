import pytest
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
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
        self, result_id_card_one: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = result_id_card_one
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_card_one")

    def test_result_id_simpletext(
        self, result_id_simpletext: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = result_id_simpletext
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/id_simpletext")

    def test_result_id_uri(self, result_id_uri: tuple[Graph, Graph, ResourceValidationReportIdentifiers]) -> None:
        res_g, onto_data_g, _ = result_id_uri
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/id_uri")

    def test_result_geoname_not_number(
        self, result_geoname_not_number: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = result_geoname_not_number
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].res_iri == URIRef("http://data/geoname_not_number")

    def test_result_id_closed_constraint(
        self, result_id_closed_constraint: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = result_id_closed_constraint
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_closed_constraint")

    def test_result_id_max_card(
        self, result_id_max_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res_g, onto_data_g, _ = result_id_max_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].res_iri == URIRef("http://data/id_max_card")


class TestQueryWithoutDetail:
    def test_result_id_card_one(
        self, result_id_card_one: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = result_id_card_one
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.MinCountConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testBoolean
        assert result.results_message == "1"
        assert not result.value

    def test_result_id_closed_constraint(
        self, result_id_closed_constraint: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = result_id_closed_constraint
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
        self, result_id_max_card: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = result_id_max_card
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.MaxCountConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.results_message == "1"
        assert not result.value

    def test_result_empty_label(
        self, result_empty_label: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, _, ids = result_empty_label
        result = _query_without_detail(ids, res)
        assert result.source_constraint_component == SH.PatternConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == RDFS.label
        assert result.results_message == "The label must be a non-empty string"
        assert result.value == " "


class TestQueryWithDetail:
    def test_result_id_simpletext(
        self, result_id_simpletext: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = result_id_simpletext
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testTextarea
        assert result.results_message == "TextValue without formatting"
        assert result.detail_bn_component == SH.MinCountConstraintComponent
        assert result.value_type == KNORA_API.TextValue
        assert not result.value

    def test_result_id_uri(self, result_id_uri: tuple[Graph, Graph, ResourceValidationReportIdentifiers]) -> None:
        res, data, ids = result_id_uri
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testUriValue
        assert result.results_message == "UriValue"
        assert result.detail_bn_component == SH.ClassConstraintComponent
        assert result.value_type == KNORA_API.TextValue
        assert result.value == "http://data/value_id_uri"

    def test_result_geoname_not_number(
        self, result_geoname_not_number: tuple[Graph, Graph, ResourceValidationReportIdentifiers]
    ) -> None:
        res, data, ids = result_geoname_not_number
        result = _query_with_detail(ids, res, data)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == ids.focus_node_iri
        assert result.res_class == ids.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.results_message == "The value must be a valid geoname code"
        assert result.detail_bn_component == SH.PatternConstraintComponent
        assert result.value_type == KNORA_API.GeonameValue
        assert result.value == "this-is-not-a-valid-code"


class TestReformatWithoutDetail:
    def test_min(self, violation_min_card: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(violation_min_card)
        assert isinstance(result, MinCardinalityViolation)
        assert result.res_id == "id_min_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_cardinality == "1-n"

    def test_max(self, violation_max_card: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(violation_max_card)
        assert isinstance(result, MaxCardinalityViolation)
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected_cardinality == "0-1"

    def test_violation_empty_label(self, violation_empty_label: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(violation_empty_label)
        assert isinstance(result, ContentRegexViolation)
        assert result.res_id == "empty_label"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "rdfs:label"
        assert result.expected_format == "The label must be a non-empty string"
        assert not result.actual_content

    def test_closed(self, violation_closed: ResultWithoutDetail) -> None:
        result = _reformat_one_without_detail(violation_closed)
        assert isinstance(result, NonExistentCardinalityViolation)
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"


class TestReformatWithDetail:
    def test_value_type(self, violation_value_type: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(violation_value_type)
        assert isinstance(result, ValueTypeViolation)
        assert result.res_id == "id_2"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testColor"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "ColorValue"

    def test_violation_regex(self, violation_regex: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(violation_regex)
        assert isinstance(result, ContentRegexViolation)
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_format == "The value must be a valid geoname code"
        assert result.actual_content == "this-is-not-a-valid-code"

    def test_unknown(self, violation_unknown_content: ResultWithDetail) -> None:
        result = _reformat_one_with_detail(violation_unknown_content)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


if __name__ == "__main__":
    pytest.main([__file__])
