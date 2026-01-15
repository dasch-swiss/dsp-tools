

from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import KnoraObjectType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_cardinalities
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_cardinality
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_class
from dsp_tools.commands.create.parsing.parse_ontology import _parse_one_property
from dsp_tools.commands.create.parsing.parse_ontology import parse_ontology
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from test.unittests.commands.create.constants import ONTO_IRI_STR
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR


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
        result = _parse_one_property(prop, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_NAMESPACE_STR}testDate"
        assert result.labels == p_lbl
        assert result.comments == p_cmnt
        assert set(result.supers) == {f"{KNORA_API_PREFIX}hasValue", "http://otherOntology.com/onto/externalDate"}
        assert result.object == KnoraObjectType.DATE
        assert result.subject is None
        assert result.gui_element == GuiElement.DATE
        assert result.node_name is None
        assert result.onto_iri == ONTO_IRI_STR

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
        result = _parse_one_property(prop, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_NAMESPACE_STR}testListProp"
        assert result.labels == p_lbl
        assert result.comments is None
        assert result.supers == [f"{KNORA_API_PREFIX}hasValue"]
        assert result.object == KnoraObjectType.LIST
        assert result.subject is None
        assert result.gui_element == GuiElement.LIST
        assert result.node_name == "node_name"
        assert result.onto_iri == ONTO_IRI_STR

    def test_good_link(self, prefixes):
        p_lbl = {"en": "testHasLinkToClassMixedCard"}
        prop = {
            "name": "testHasLinkToClassMixedCard",
            "super": ["hasLinkTo", ":internalSuper"],
            "object": ":ClassMixedCard",
            "labels": p_lbl,
            "gui_element": "Searchbox",
        }
        result = _parse_one_property(prop, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, ParsedProperty)
        assert result.name == f"{ONTO_NAMESPACE_STR}testHasLinkToClassMixedCard"
        assert result.labels == p_lbl
        assert result.comments is None
        assert set(result.supers) == {f"{KNORA_API_PREFIX}hasLinkTo", f"{ONTO_NAMESPACE_STR}internalSuper"}
        assert result.object == f"{ONTO_NAMESPACE_STR}ClassMixedCard"
        assert result.subject is None
        assert result.gui_element == GuiElement.SEARCHBOX
        assert result.node_name is None
        assert result.onto_iri == ONTO_IRI_STR

    def test_bad_prefix(self, prefixes):
        p_lbl = {"en": "testHasLinkToClassMixedCard"}
        prop = {
            "name": "testHasLinkToClassMixedCard",
            "super": ["hasLinkTo", "inexistent:internalSuper"],
            "object": ":ClassMixedCard",
            "labels": p_lbl,
            "gui_element": "Searchbox",
        }
        result = _parse_one_property(prop, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, list)
        assert len(result) == 1
        prob = result.pop()
        assert (
            prob.problematic_object == 'At property "testHasLinkToClassMixedCard" / Super: "inexistent:internalSuper"'
        )
        assert prob.problem == InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED


class TestParseClasses:
    def test_good_str_super(self, prefixes):
        lbl = {"en": "ArchiveRepresentation"}
        cmnt = {"en": "This is a comment"}
        cls = {"name": "TestArchiveRepresentation", "super": "ArchiveRepresentation", "labels": lbl, "comments": cmnt}
        result = _parse_one_class(cls, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, ParsedClass)
        assert result.name == f"{ONTO_NAMESPACE_STR}TestArchiveRepresentation"
        assert result.labels == lbl
        assert result.comments == cmnt
        assert result.supers == [f"{KNORA_API_PREFIX}ArchiveRepresentation"]

    def test_good_list_super(self, prefixes):
        lbl = {"en": "ArchiveRepresentation"}
        cls = {
            "name": "TestArchiveRepresentation",
            "super": ["ArchiveRepresentation", ":OntoClass"],
            "labels": lbl,
        }
        result = _parse_one_class(cls, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, ParsedClass)
        assert result.name == f"{ONTO_NAMESPACE_STR}TestArchiveRepresentation"
        assert result.labels == lbl
        assert result.comments is None
        assert set(result.supers) == {f"{KNORA_API_PREFIX}ArchiveRepresentation", f"{ONTO_NAMESPACE_STR}OntoClass"}

    def test_cannot_resolve_prefix(self, prefixes):
        lbl = {"en": "ArchiveRepresentation"}
        cmnt = {"en": "This is a comment"}
        cls = {"name": "TestArchiveRepresentation", "super": "inexistent:Cls", "labels": lbl, "comments": cmnt}
        result = _parse_one_class(cls, ONTO_NAMESPACE_STR, prefixes)
        assert isinstance(result, list)
        assert len(result) == 1
        problem = result.pop(0)
        assert isinstance(problem, CreateProblem)
        assert problem.problematic_object == 'At class "TestArchiveRepresentation" / Super: "inexistent:Cls"'
        assert problem.problem == InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED


class TestParseCardinalities:
    def test_parse_cardinalities_with_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": ":testSimpleText", "cardinality": "0-n"}],
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_NAMESPACE_STR, prefixes)
        assert len(parsed) == 1
        assert len(failures) == 0
        result = parsed.pop(0)
        assert result.class_iri == f"{ONTO_NAMESPACE_STR}TestArchiveRepresentation"
        assert len(result.cards) == 1

    def test_parse_cardinalities_no_cards(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_NAMESPACE_STR, prefixes)
        assert len(parsed) == 0
        assert len(failures) == 0

    def test_parse_cardinalities_failure(self, prefixes):
        cls = {
            "name": "TestArchiveRepresentation",
            "super": "ArchiveRepresentation",
            "labels": {"en": "ArchiveRepresentation"},
            "cardinalities": [{"propname": "inexistent:testSimpleText", "cardinality": "0-n"}],
        }
        parsed, failures = _parse_cardinalities([cls], ONTO_NAMESPACE_STR, prefixes)
        assert len(parsed) == 0
        assert len(failures) == 1
        result = failures.pop(0)
        assert isinstance(result, CreateProblem)
        assert result.problematic_object == "inexistent:testSimpleText"
        assert result.problem == InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED

    def test_0_1(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-1", "gui_order": 0}
        result = _parse_one_cardinality(card, ONTO_NAMESPACE_STR, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_NAMESPACE_STR}testBoolean"
        assert result.cardinality == Cardinality.C_0_1
        assert result.gui_order == 0

    def test_1(self, prefixes):
        card = {"propname": "onto:testBoolean", "cardinality": "1", "gui_order": 3}
        result = _parse_one_cardinality(card, ONTO_NAMESPACE_STR, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_NAMESPACE_STR}testBoolean"
        assert result.cardinality == Cardinality.C_1
        assert result.gui_order == 3

    def test_0_n(self, prefixes):
        card = {"propname": ":testBoolean", "cardinality": "0-n"}
        result = _parse_one_cardinality(card, ONTO_NAMESPACE_STR, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{ONTO_NAMESPACE_STR}testBoolean"
        assert result.cardinality == Cardinality.C_0_N
        assert result.gui_order is None

    def test_1_n(self, prefixes):
        card = {"propname": "seqnum", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_NAMESPACE_STR, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, ParsedPropertyCardinality)
        assert result.propname == f"{KNORA_API_PREFIX}seqnum"
        assert result.cardinality == Cardinality.C_1_N
        assert result.gui_order == 2

    def test_fail(self, prefixes):
        card = {"propname": "inexistent:prefix", "cardinality": "1-n", "gui_order": 2}
        result = _parse_one_cardinality(card, ONTO_NAMESPACE_STR, prefixes)  # type: ignore[arg-type]
        assert isinstance(result, CreateProblem)
        assert result.problematic_object == "inexistent:prefix"
        assert result.problem == InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED
