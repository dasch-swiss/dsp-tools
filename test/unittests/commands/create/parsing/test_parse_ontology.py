# mypy: disable-error-code="no-untyped-def"

from dsp_tools.commands.create.constants import KNORA_API_STR
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_cardinalities
from dsp_tools.commands.create.parsing.parse_ontology import _parse_classes
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_cardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_property
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from test.unittests.commands.create.parsing.fixtures import ONTO_NAME
from test.unittests.commands.create.parsing.fixtures import ONTO_PREFIX


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
                    "name": "TestArchiveRepresentation",
                    "super": "ArchiveRepresentation",
                    "labels": {"en": "ArchiveRepresentation"},
                    "cardinalities": [{"propname": "inexistent:testSimpleText", "cardinality": "0-n"}],
                }
            ],
        }
        result = parse_ontology(onto_wrong, prefixes)
        assert isinstance(result, CollectedProblems)
        assert len(result.problems) == 1


class TestParseProperties:
    def test_good_with_comment(self, prefixes):
        p_lbl = {"en": "Super Property Date"}
        p_cmnt = {"en": "Comment on property"}
        prop = {
            "name": "testDate",
            "super": ["hasValue", "externalOnto:externalDate"],
            "object": "DateValue",
            "labels": p_lbl,
            "comments": p_cmnt,
            "gui_element": "Date",
        }
        result = _parse_one_property(prop, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_PREFIX}testDate"
        assert result.labels == p_lbl
        assert result.comments == p_cmnt
        assert set(result.supers) == {f"{KNORA_API_STR}hasValue", "http://otherOntology.com/onto/externalDate"}
        assert result.object == KnoraObjectType.DATE
        assert result.subject is None
        assert result.gui_element == GuiElement.DATE
        assert result.node_name is None
        assert result.onto_name == ONTO_NAME

    def test_good_list(self, prefixes):
        p_lbl = {"en": "Test List"}
        prop = {
            "name": "testListProp",
            "super": ["hasValue"],
            "object": "ListValue",
            "labels": p_lbl,
            "gui_element": "List",
            "gui_attributes": {"hlist": "node_name"},
        }
        result = _parse_one_property(prop, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_PREFIX}testListProp"
        assert result.labels == p_lbl
        assert result.comments is None
        assert result.supers == [f"{KNORA_API_STR}hasValue"]
        assert result.object == KnoraObjectType.LIST
        assert result.subject is None
        assert result.gui_element == GuiElement.LIST
        assert result.node_name == "node_name"
        assert result.onto_name == ONTO_NAME

    def test_good_link(self, prefixes):
        p_lbl = {"en": "testHasLinkToClassMixedCard"}
        prop = {
            "name": "testHasLinkToClassMixedCard",
            "super": ["hasLinkTo", ":internalSuper"],
            "object": ":ClassMixedCard",
            "labels": p_lbl,
            "gui_element": "Searchbox",
        }
        result = _parse_one_property(prop, ONTO_PREFIX, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_PREFIX}testHasLinkToClassMixedCard"
        assert result.labels == p_lbl
        assert result.comments is None
        assert set(result.supers) == {f"{KNORA_API_STR}hasLinkTo", f"{ONTO_PREFIX}internalSuper"}
        assert result.object == f"{ONTO_PREFIX}ClassMixedCard"
        assert result.subject is None
        assert result.gui_element == GuiElement.SEARCHBOX
        assert result.node_name is None
        assert result.onto_name == ONTO_NAME

    def test_bad_prefix(self, prefixes):
        p_lbl = {"en": "testHasLinkToClassMixedCard"}
        prop = {
            "name": "testHasLinkToClassMixedCard",
            "super": ["hasLinkTo", "inexistent:internalSuper"],
            "object": ":ClassMixedCard",
            "labels": p_lbl,
            "gui_element": "Searchbox",
        }
        result = _parse_one_property(prop, ONTO_PREFIX, prefixes)
        assert isinstance(result, list)
        assert len(result) == 1
        prob = result.pop()
        assert (
            prob.problematic_object == 'At property "testHasLinkToClassMixedCard" / Super: "inexistent:internalSuper"'
        )
        assert prob.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED


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
        assert result.class_iri == f"{ONTO_PREFIX}TestArchiveRepresentation"
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
        assert isinstance(result, CreateProblem)
        assert result.problematic_object == "inexistent:testSimpleText"
        assert result.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED

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
        assert result.propname == f"{KNORA_API_STR}seqnum"
        assert result.cardinality == Cardinality.C_1_N
        assert result.gui_order == 2

    def test_fail(self, prefixes):
        card = {"propname": "inexistent:prefix", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_PREFIX, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, CreateProblem)
        assert result.problematic_object == "inexistent:prefix"
        assert result.problem == ProblemType.PREFIX_COULD_NOT_BE_RESOLVED
