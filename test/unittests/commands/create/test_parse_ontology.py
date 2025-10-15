import pytest

from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality

ONTO_PREFIX = "http://0.0.0.0:3333/ontology/8888/onto/v2#"

from dsp_tools.commands.create.parsing.parse_ontology import _parse_cardinalities
from dsp_tools.commands.create.parsing.parse_ontology import _parse_classes
from dsp_tools.commands.create.parsing.parse_ontology import _parse_properties


class TestParseOntology: ...


class TestParseProperties:
    def test_good(self):
        prop = {"detail": "to-be-implemented"}
        resources = {"properties": [prop]}
        parsed, problems = _parse_properties(resources)
        assert len(parsed) == 1
        assert not problems


class TestParseClasses:
    def test_good(self, prefixes):
        cls = {"detail": "to-be-implemented"}
        resources = {"resources": [cls]}
        parsed, problems = _parse_classes(resources)
        assert len(parsed) == 1
        assert not problems


class TestParseCardinalities:
    def test_0_1(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-1", "gui_order": 0}
        result = _parse_cardinalities(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == ""
        assert result.cardinality == Cardinality
        assert result.gui_order == 0

    def test_1(self, prefixes):
        card = {"propname": "onto:testBoolean", "cardinality": "1", "gui_order": 3}
        result = _parse_cardinalities(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == ""
        assert result.cardinality == Cardinality
        assert result.gui_order == 3

    def test_0_n(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-n"}
        result = _parse_cardinalities(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == ""
        assert result.cardinality == Cardinality
        assert result.gui_order is None

    def test_1_n(self, prefixes):
        card = {"propname": "seqnum", "cardinality": "1-n", "gui_order": 2}
        result = _parse_cardinalities(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == ""
        assert result.cardinality == Cardinality
        assert result.gui_order == 2

    def test_fail(self, prefixes):
        card = {"propname": "inexistent:prefix", "cardinality": "1-n", "gui_order": 2}
        result = _parse_cardinalities(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, InputProblem)
        assert result.problematic_object == "inexistent:prefix"
        assert result.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED


class TestResolvePrefix:
    @pytest.mark.parametrize(
        "prefixed_iri",
        [
            "",
            "",
            "",
            "",
        ],
    )
    def test_good(self, prefixed_iri, prefixes):
        pass

    @pytest.mark.parametrize(
        "prefixed_iri",
        [
            "",
            "",
            "",
            "",
        ],
    )
    def test_fail(self, prefixed_iri, prefixes):
        pass
