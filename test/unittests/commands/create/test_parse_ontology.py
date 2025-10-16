# mypy: disable-error-code="no-untyped-def"

from dsp_tools.commands.create.constants import KNORA_API
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_cardinalities
from dsp_tools.commands.create.parsing.parse_ontology import _parse_classes
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_cardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_properties
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from test.unittests.commands.create.fixtures import ONTO_PREFIX


class TestParseOntology:
    def test_good(self, onto_json, prefixes):
        result = parse_ontology(onto_json, prefixes)
        assert isinstance(result, ParsedOntology)

    def test_fail(self, prefixes):
        onto_wrong = {
            "name": "onto",
            "label": "Ontology",
            "properties": [],
            "resources": [
                {
                    "name": "inexistent:TestArchiveRepresentation",
                    "super": "ArchiveRepresentation",
                    "labels": {"en": "ArchiveRepresentation"},
                }
            ],
        }
        result = parse_ontology(onto_wrong, prefixes)
        assert isinstance(result, CollectedProblems)
        assert len(result.problems) == 1


class TestParseProperties:
    def test_good(self):
        prop = {
            "name": "testGeoname",
            "super": ["hasValue"],
            "object": "GeonameValue",
            "labels": {"en": "Test Geoname"},
            "gui_element": "Geonames",
        }
        parsed, problems = _parse_properties([prop], ONTO_PREFIX)
        assert len(parsed) == 1
        assert not problems


class TestParseClasses:
    def test_good(self):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
        }
        parsed, problems = _parse_classes([cls], ONTO_PREFIX)
        assert len(parsed) == 1
        assert not problems


class TestParseCardinalities:
    def test_parse_cardinalities_with_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": ":testSimpleText", "cardinality": "0-n"}],
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_PREFIX, prefixes)
        assert len(parsed) == 1
        assert len(failures) == 0
        result = parsed.pop(0)
        assert result.class_iri == f"{KNORA_API}TestArchiveRepresentation"
        assert len(result.cards) == 1

    def test_parse_cardinalities_no_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_PREFIX, prefixes)
        assert len(parsed) == 0
        assert len(failures) == 0

    def test_parse_cardinalities_failure(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": "inexistent:testSimpleText", "cardinality": "0-n"}],
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_PREFIX, prefixes)
        assert len(parsed) == 0
        assert len(failures) == 1
        result = failures.pop(0)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_0_1(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-1", "gui_order": 0}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_0_1
        assert result.gui_order == 0

    def test_1(self, prefixes):
        card = {"propname": "onto:testBoolean", "cardinality": "1", "gui_order": 3}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_1
        assert result.gui_order == 3

    def test_0_n(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-n"}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_0_N
        assert result.gui_order is None

    def test_1_n(self, prefixes):
        card = {"propname": "seqnum", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{KNORA_API}seqnum"
        assert result.cardinality == Cardinality.C_1_N
        assert result.gui_order == 2

    def test_fail(self, prefixes):
        card = {"propname": "inexistent:prefix", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, InputProblem)
        assert result.problematic_object == "inexistent:prefix"
        assert result.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED
