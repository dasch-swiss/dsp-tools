from dsp_tools.commands.mapping.models import ParsedClassMapping
from dsp_tools.commands.mapping.models import ParsedMappings
from dsp_tools.commands.mapping.models import ParsedPropertyMapping
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.commands.mapping.resolve_parsed_mappings import _resolve_one_mapping
from dsp_tools.commands.mapping.resolve_parsed_mappings import _resolve_prefixed_iri
from dsp_tools.commands.mapping.resolve_parsed_mappings import resolve_parsed_mappings

ONTO_NS = "http://0.0.0.0:3333/ontology/0001/onto/v2#"
PREFIX_LOOKUP = {"schema": "http://schema.org/"}


class TestResolvePrefixedIri:
    def test_valid_uri_returned_as_is(self):
        result = _resolve_prefixed_iri("http://schema.org/Book", {}, "Book")
        assert result == "http://schema.org/Book"

    def test_no_colon_returns_problem(self):
        result = _resolve_prefixed_iri("Book", {}, "Book")
        assert isinstance(result, PrefixResolutionProblem)
        assert result.input_value == "Book"

    def test_empty_prefix_returns_problem(self):
        result = _resolve_prefixed_iri(":Book", {}, "Book")
        assert isinstance(result, PrefixResolutionProblem)
        assert result.input_value == ":Book"

    def test_empty_local_name_returns_problem(self):
        result = _resolve_prefixed_iri("schema:", PREFIX_LOOKUP, "Book")
        assert isinstance(result, PrefixResolutionProblem)
        assert result.input_value == "schema:"

    def test_prefix_not_in_lookup_returns_problem(self):
        result = _resolve_prefixed_iri("owl:Class", PREFIX_LOOKUP, "Book")
        assert isinstance(result, PrefixResolutionProblem)
        assert result.input_value == "owl:Class"

    def test_known_prefix_resolves_to_iri(self):
        result = _resolve_prefixed_iri("schema:Book", PREFIX_LOOKUP, "Book")
        assert result == "http://schema.org/Book"


class TestResolveOneMapping:
    def test_all_iris_resolved_class(self):
        parsed = ParsedClassMapping("Book", ["schema:Book"])
        resolved, problems = _resolve_one_mapping(parsed, PREFIX_LOOKUP, ONTO_NS, ResolvedClassMapping)
        assert isinstance(resolved, ResolvedClassMapping)
        assert resolved.iri == f"{ONTO_NS}Book"
        assert resolved.mapping_iris == ["http://schema.org/Book"]
        assert problems == []

    def test_all_iris_resolved_property(self):
        parsed = ParsedPropertyMapping("hasTitle", ["schema:name"])
        resolved, problems = _resolve_one_mapping(parsed, PREFIX_LOOKUP, ONTO_NS, ResolvedPropertyMapping)
        assert isinstance(resolved, ResolvedPropertyMapping)
        assert resolved.iri == f"{ONTO_NS}hasTitle"
        assert resolved.mapping_iris == ["http://schema.org/name"]
        assert problems == []

    def test_invalid_iri_excluded_and_problem_returned(self):
        parsed = ParsedClassMapping("Book", ["no_colon"])
        resolved, problems = _resolve_one_mapping(parsed, PREFIX_LOOKUP, ONTO_NS, ResolvedClassMapping)
        assert resolved.mapping_iris == []
        assert len(problems) == 1

    def test_mixed_valid_and_invalid(self):
        parsed = ParsedClassMapping("Book", ["schema:Book", "no_colon"])
        resolved, problems = _resolve_one_mapping(parsed, PREFIX_LOOKUP, ONTO_NS, ResolvedClassMapping)
        assert resolved.mapping_iris == ["http://schema.org/Book"]
        assert len(problems) == 1


class TestResolveParsedMappings:
    def test_resolves_classes_and_properties(self):
        parsed = ParsedMappings(
            classes=[ParsedClassMapping("Book", ["schema:Book"])],
            properties=[ParsedPropertyMapping("hasTitle", ["schema:name"])],
        )
        resolved, problems = resolve_parsed_mappings(parsed, PREFIX_LOOKUP, ONTO_NS)
        assert len(resolved.classes) == 1
        assert resolved.classes[0].iri == f"{ONTO_NS}Book"
        assert resolved.classes[0].mapping_iris == ["http://schema.org/Book"]
        assert len(resolved.properties) == 1
        assert resolved.properties[0].iri == f"{ONTO_NS}hasTitle"
        assert resolved.properties[0].mapping_iris == ["http://schema.org/name"]
        assert problems == []

    def test_problems_accumulated(self):
        parsed = ParsedMappings(
            classes=[ParsedClassMapping("Book", ["schema:Book"])],
            properties=[ParsedPropertyMapping("hasTitle", ["no_colon"])],
        )
        _, problems = resolve_parsed_mappings(parsed, PREFIX_LOOKUP, ONTO_NS)
        assert len(problems) == 1
        assert isinstance(problems[0], PrefixResolutionProblem)
