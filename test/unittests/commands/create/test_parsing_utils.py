# mypy: disable-error-code="no-untyped-def"

import pytest

from dsp_tools.commands.create.constants import KNORA_API
from dsp_tools.commands.create.parsing.parsing_utils import resolve_prefix
from test.unittests.commands.create.fixtures import ONTO_PREFIX


class TestResolvePrefix:
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
        result = resolve_prefix(prefixed_iri, ONTO_PREFIX, prefixes)
        assert result == expected

    @pytest.mark.parametrize(
        "prefixed_iri",
        [
            "inexistent:Cls",
        ],
    )
    def test_fail(self, prefixed_iri, prefixes):
        result = resolve_prefix(prefixed_iri, ONTO_PREFIX, prefixes)
        assert result is None
