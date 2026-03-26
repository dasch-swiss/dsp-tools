from dsp_tools.commands.mapping.iri_resolver import resolve_all
from dsp_tools.commands.mapping.models import ClassMapping
from dsp_tools.commands.mapping.models import ParsedMappingExcel
from dsp_tools.commands.mapping.models import PropertyMapping

_PREFIX_MAP = {
    "schema": "http://schema.org/",
    "ex": "http://example.org/",
}


def _make_excel(class_iris: list[list[str]], property_iris: list[list[str]] | None = None) -> ParsedMappingExcel:
    classes = [ClassMapping(class_iri=f"MyClass{i}", mapping_iris=iris) for i, iris in enumerate(class_iris)]
    properties = [
        PropertyMapping(property_iri=f"myProp{i}", mapping_iris=iris) for i, iris in enumerate(property_iris or [])
    ]
    return ParsedMappingExcel(classes=classes, properties=properties)


def test_full_iri_passthrough() -> None:
    excel = _make_excel([["http://schema.org/Person"]])
    resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert not problems
    assert resolved.classes[0].mapping_iris == ["http://schema.org/Person"]


def test_full_https_iri_passthrough() -> None:
    excel = _make_excel([["https://schema.org/Person"]])
    resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert not problems
    assert resolved.classes[0].mapping_iris == ["https://schema.org/Person"]


def test_prefixed_name_resolved() -> None:
    excel = _make_excel([["schema:Person"]])
    resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert not problems
    assert resolved.classes[0].mapping_iris == ["http://schema.org/Person"]


def test_unknown_prefix_collected() -> None:
    excel = _make_excel([["unknown:Person"]])
    _resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert len(problems) == 1
    assert problems[0].prefix == "unknown"
    assert problems[0].raw_value == "unknown:Person"


def test_empty_local_name_error() -> None:
    excel = _make_excel([["schema:"]])
    _resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert len(problems) == 1
    assert problems[0].prefix == "schema"
    assert problems[0].raw_value == "schema:"


def test_empty_prefix_error() -> None:
    excel = _make_excel([[":Person"]])
    _resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert len(problems) == 1
    assert problems[0].raw_value == ":Person"


def test_no_colon_error() -> None:
    excel = _make_excel([["Person"]])
    _resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert len(problems) == 1
    assert problems[0].raw_value == "Person"


def test_multiple_errors_all_collected() -> None:
    excel = _make_excel([["unknown:A", ":B", "C", "schema:Valid"]])
    resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert len(problems) == 3
    assert resolved.classes[0].mapping_iris == ["http://schema.org/Valid"]


def test_property_resolution() -> None:
    excel = _make_excel([], [["ex:name"]])
    resolved, problems = resolve_all(excel, _PREFIX_MAP)
    assert not problems
    assert resolved.properties[0].mapping_iris == ["http://example.org/name"]
