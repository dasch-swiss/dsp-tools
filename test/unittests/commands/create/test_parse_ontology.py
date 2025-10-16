# mypy: disable-error-code="no-untyped-def"

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_classes
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_cardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_class_cardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_properties
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from test.unittests.commands.create.fixtures import KNORA_API
from test.unittests.commands.create.fixtures import ONTO_PREFIX


class TestParseOntology:
    def test_good(self, project, prefixes):
        result = parse_ontology(project, prefixes)
        assert isinstance(result, ParsedOntology)

    def test_fail(self, project, prefixes):
        result = parse_ontology(project, prefixes)
        assert isinstance(result, CollectedProblems)


class TestParseProperties:
    def test_good(self, prefixes):
        prop = {
            "name": "testGeoname",
            "super": ["hasValue"],
            "object": "GeonameValue",
            "labels": {"en": "Test Geoname"},
            "gui_element": "Geonames",
        }
        parsed, problems = _parse_properties([prop], ONTO_PREFIX, prefixes)
        assert len(parsed) == 1
        assert not problems


class TestParseClasses:
    def test_good(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
        }
        parsed, problems = _parse_classes([cls], ONTO_PREFIX, prefixes)
        assert len(parsed) == 1
        assert not problems


class TestParseCardinalities:
    def test_parse_one_class_cardinality_with_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": ":testSimpleText", "cardinality": "0-n"}],
        }
        result = _parse_one_class_cardinality(cls, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedClassCardinalities)
        assert result.class_iri == f"{KNORA_API}TestArchiveRepresentation"
        assert len(result.cards) == 1

    def test_parse_one_class_cardinality_no_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
        }
        result = _parse_one_class_cardinality(cls, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedClassCardinalities)
        assert result.class_iri == f"{KNORA_API}TestArchiveRepresentation"
        assert len(result.cards) == 0

    def test_parse_one_class_cardinality_failure(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": "inexistent:testSimpleText", "cardinality": "0-n"}],
        }
        result = _parse_one_class_cardinality(cls, ONTO_PREFIX, prefixes)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_0_1(self, prefixes):
        card: dict[str, str | int] = {"propname": ":testBoolean", "cardinality": "0-1", "gui_order": 0}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_0_1
        assert result.gui_order == 0

    def test_1(self, prefixes):
        card: dict[str, str | int] = {"propname": "onto:testBoolean", "cardinality": "1", "gui_order": 3}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_1
        assert result.gui_order == 3

    def test_0_n(self, prefixes):
        card: dict[str, str | int] = {"propname": ":testBoolean", "cardinality": "0-n"}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_PREFIX}testBoolean"
        assert result.cardinality == Cardinality.C_0_N
        assert result.gui_order is None

    def test_1_n(self, prefixes):
        card: dict[str, str | int] = {"propname": "seqnum", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{KNORA_API}seqnum"
        assert result.cardinality == Cardinality.C_1_N
        assert result.gui_order == 2

    def test_fail(self, prefixes):
        card: dict[str, str | int] = {"propname": "inexistent:prefix", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)
        assert isinstance(result, InputProblem)
        assert result.problematic_object == "inexistent:prefix"
        assert result.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED
