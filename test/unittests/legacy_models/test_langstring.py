"""unit tests for langstrings"""

import unittest

import pytest

from dsp_tools.legacy_models.langstring import Languages
from dsp_tools.legacy_models.langstring import create_lang_string
from dsp_tools.legacy_models.langstring import create_lang_string_from_json
from dsp_tools.legacy_models.langstring import create_lang_string_from_json_ld

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestLangString(unittest.TestCase):
    simple_string_de = "Ein simpler String"
    simple_string_fr = "Quelque chose en français"
    test_string_en = "This is a test"
    test_string_de = "Das ist ein Test"

    def test_langstring_instantiation1(self) -> None:
        """Test a LangString without language."""
        ls = create_lang_string(self.simple_string_de)
        self.assertEqual(ls[None], self.simple_string_de)

    def test_langstring_instantiation2(self) -> None:
        """Test a LangString using string and Languages-enums as index."""
        ls = create_lang_string({"de": self.simple_string_de, "fr": self.simple_string_fr})
        self.assertEqual(ls["de"], self.simple_string_de)
        self.assertEqual(ls[Languages.FR], self.simple_string_fr)

    def test_langstring_instantiation3(self) -> None:
        """Test a LangString using string and Languages-enums as index."""
        ls = create_lang_string({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        self.assertEqual(ls[Languages.DE], self.simple_string_de)
        self.assertEqual(ls["fr"], self.simple_string_fr)

    def test_langstring_fromjson(self) -> None:
        """Test reading a LangString from JSON as used in Knora Admin."""
        test = [{"language": "en", "value": self.test_string_en}, {"language": "de", "value": self.test_string_de}]
        ls = create_lang_string_from_json(test)
        assert ls is not None
        self.assertEqual(ls["de"], self.test_string_de)
        self.assertEqual(ls[Languages.EN], self.test_string_en)

    def test_langstring_fromjsonld(self) -> None:
        """Test reading a LangString from JSON-LD as used in Knora data/ontologies"""
        test = [{"@language": "en", "@value": self.test_string_en}, {"@language": "de", "@value": self.test_string_de}]
        ls = create_lang_string_from_json_ld(test)
        assert ls is not None
        self.assertEqual(ls["de"], self.test_string_de)
        self.assertEqual(ls[Languages.EN], self.test_string_en)

    def test_langstring_emptyness(self) -> None:
        """Test if emptyness is detected."""
        ls = create_lang_string()
        self.assertTrue(ls.is_empty())


if __name__ == "__main__":
    pytest.main([__file__])
