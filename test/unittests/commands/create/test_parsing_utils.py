# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.create.constants import KNORA_API
from dsp_tools.commands.create.parsing.parsing_utils import create_prefix_lookup
from dsp_tools.commands.create.parsing.parsing_utils import resolve_to_absolute_iri
from test.unittests.commands.create.fixtures import ONTO_PREFIX

EXTERNAL_PREFIXES = {
    "wrong-ending": "http://wrong-ending.org/onto",
    "with-slash": "http://with-slash.org/onto/",
    "with-hashtag": "http://with-hashtag.org/onto#",
}


class TestPrefixLookup:
    def test_with_prefixes(self):
        project_json = {
            "prefixes": EXTERNAL_PREFIXES,
            "project": {"shortcode": "8888", "ontologies": [{"name": "onto"}]},
        }
        expected = {}
        result = create_prefix_lookup(project_json, "http://0.0.0.0:3333")
        assert result == expected

    def test_without_prefixes(self):
        project_json = {"project": {"shortcode": "8888", "ontologies": [{"name": "onto1"}, {"name": "onto2"}]}}
        expected = {}
        result = create_prefix_lookup(project_json, "http://0.0.0.0:3333")
        assert result == expected


class TestResolveToAbsoluteIri:
    @pytest.mark.parametrize(
        ("prefixed_iri", "expected"),
        [
            ("hasValue", f"{KNORA_API}hasValue"),
            ("knora-api:hasValue", f"{KNORA_API}hasValue"),
            ("onto:testBool", f"{ONTO_PREFIX}testBool"),
            (":testBool", f"{ONTO_PREFIX}testBool"),
            ("http://purl.org/dc/terms/title", "http://purl.org/dc/terms/title"),
            (f"{KNORA_API}hasValue", f"{KNORA_API}hasValue"),
        ],
    )
    def test_good(self, prefixed_iri, expected, prefixes):
        result = resolve_to_absolute_iri(prefixed_iri, ONTO_PREFIX, prefixes)
        assert result == expected

    @pytest.mark.parametrize(
        "prefixed_iri",
        [
            "inexistent:Cls",
        ],
    )
    def test_fail(self, prefixed_iri, prefixes):
        result = resolve_to_absolute_iri(prefixed_iri, ONTO_PREFIX, prefixes)
        assert result is None
