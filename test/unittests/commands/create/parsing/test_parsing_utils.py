# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.create.parsing.parsing_utils import create_prefix_lookup
from dsp_tools.commands.create.parsing.parsing_utils import resolve_to_absolute_iri
from dsp_tools.utils.rdf_constants import DSP_NAME_TO_PREFIX
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from dsp_tools.utils.rdf_constants import SALSAH_GUI_PREFIX
from test.unittests.commands.create.constants import ONTO_NAMESPACE_STR

EXTERNAL_PREFIXES = {
    "wrong-ending": "http://wrong-ending.org/onto",
    "with-slash": "http://with-slash.org/onto/",
    "with-hashtag": "http://with-hashtag.org/onto#",
} | DSP_NAME_TO_PREFIX


class TestPrefixLookup:
    def test_with_prefixes(self):
        project_json = {
            "prefixes": EXTERNAL_PREFIXES,
            "project": {"shortcode": "0003", "ontologies": [{"name": "onto"}]},
        }
        expected = {
            "knora-api": KNORA_API_PREFIX,
            "salsah-gui": SALSAH_GUI_PREFIX,
            "onto": "http://0.0.0.0:3333/ontology/0003/onto/v2#",
            "with-hashtag": "http://with-hashtag.org/onto#",
            "with-slash": "http://with-slash.org/onto/",
            "wrong-ending": "http://wrong-ending.org/onto/",
        }
        result = create_prefix_lookup(project_json, "http://0.0.0.0:3333")
        assert result == expected

    def test_without_prefixes(self):
        project_json = {"project": {"shortcode": "0003", "ontologies": [{"name": "onto1"}, {"name": "onto2"}]}}
        expected = {
            "knora-api": KNORA_API_PREFIX,
            "salsah-gui": SALSAH_GUI_PREFIX,
            "onto1": "http://0.0.0.0:3333/ontology/0003/onto1/v2#",
            "onto2": "http://0.0.0.0:3333/ontology/0003/onto2/v2#",
        }
        result = create_prefix_lookup(project_json, "http://0.0.0.0:3333")
        assert result == expected


class TestResolveToAbsoluteIri:
    @pytest.mark.parametrize(
        ("prefixed_iri", "expected"),
        [
            ("hasValue", f"{KNORA_API_PREFIX}hasValue"),
            ("knora-api:hasValue", f"{KNORA_API_PREFIX}hasValue"),
            ("onto:testBool", f"{ONTO_NAMESPACE_STR}testBool"),
            (":testBool", f"{ONTO_NAMESPACE_STR}testBool"),
            ("http://purl.org/dc/terms/title", "http://purl.org/dc/terms/title"),
            (f"{KNORA_API_PREFIX}hasValue", f"{KNORA_API_PREFIX}hasValue"),
        ],
    )
    def test_good(self, prefixed_iri, expected, prefixes):
        result = resolve_to_absolute_iri(prefixed_iri, ONTO_NAMESPACE_STR, prefixes)
        assert result == expected

    @pytest.mark.parametrize(
        "prefixed_iri",
        [
            "inexistent:Cls",
        ],
    )
    def test_fail(self, prefixed_iri, prefixes):
        result = resolve_to_absolute_iri(prefixed_iri, ONTO_NAMESPACE_STR, prefixes)
        assert result is None
