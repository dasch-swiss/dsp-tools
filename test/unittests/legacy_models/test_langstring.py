"""unit tests for langstrings"""

import unittest

import pytest

from dsp_tools.legacy_models.langstring import LangString
from dsp_tools.legacy_models.langstring import Languages

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestLangString(unittest.TestCase):
    simple_string_de = "Ein simpler String"
    simple_string_fr = "Quelque chose en français"
    test_string_en = "This is a test"
    test_string_de = "Das ist ein Test"

    def test_langstring_instantiation1(self) -> None:
        """Test a LangString without language."""
        ls = LangString(self.simple_string_de)
        self.assertEqual(ls[None], self.simple_string_de)

    def test_langstring_instantiation2(self) -> None:
        """Test a LangString using string and Languages-enums as index."""
        ls = LangString({"de": self.simple_string_de, "fr": self.simple_string_fr})
        self.assertEqual(ls["de"], self.simple_string_de)
        self.assertEqual(ls[Languages.FR], self.simple_string_fr)

    def test_langstring_instantiation3(self) -> None:
        """Test a LangString using string and Languages-enums as index."""
        ls = LangString({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        self.assertEqual(ls[Languages.DE], self.simple_string_de)
        self.assertEqual(ls["fr"], self.simple_string_fr)

    def test_langstring_change(self) -> None:
        """test if changing a LangString item works."""
        ls = LangString({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        ls["de"] = "gagaga"
        self.assertEqual(ls[Languages.DE], "gagaga")
        self.assertEqual(ls["fr"], self.simple_string_fr)

    def test_langstring_fromjson(self) -> None:
        """Test reading a LangString from JSON as used in Knora Admin."""
        test = [{"language": "en", "value": self.test_string_en}, {"language": "de", "value": self.test_string_de}]
        ls = LangString.fromJsonObj(test)
        self.assertEqual(ls["de"], self.test_string_de)
        self.assertEqual(ls[Languages.EN], self.test_string_en)

    def test_langstring_fromjsonld(self) -> None:
        """Test reading a LangString from JSON-LD as used in Knora data/ontologies"""
        test = [{"@language": "en", "@value": self.test_string_en}, {"@language": "de", "@value": self.test_string_de}]
        ls = LangString.fromJsonLdObj(test)
        self.assertEqual(ls["de"], self.test_string_de)
        self.assertEqual(ls[Languages.EN], self.test_string_en)

    def test_langstring_tojson(self) -> None:
        """Test converting a LangString to JSON and JSON-LD"""
        ls = LangString(self.simple_string_de)
        json = ls.toJsonObj()
        self.assertEqual(json, self.simple_string_de)
        json = ls.toJsonLdObj()
        self.assertEqual(json, self.simple_string_de)

        ls = LangString({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        json = ls.toJsonObj()
        expected = [
            {"language": "de", "value": self.simple_string_de},
            {"language": "fr", "value": self.simple_string_fr},
        ]
        self.assertEqual(json, expected)
        jsonld = ls.toJsonLdObj()
        expected = [
            {"@language": "de", "@value": self.simple_string_de},
            {"@language": "fr", "@value": self.simple_string_fr},
        ]
        self.assertEqual(jsonld, expected)

    def test_langstring_emptyness(self) -> None:
        """Test if a LanGstring can be emptied and if the emptyness is detected."""
        ls = LangString()
        self.assertTrue(ls.isEmpty())
        ls = LangString(self.simple_string_de)
        ls.empty()
        self.assertTrue(ls.isEmpty())
        ls = LangString({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        ls.empty()
        self.assertTrue(ls.isEmpty())

    def test_langstring_iterator(self) -> None:
        """Test iterating over a LangString."""
        ls = LangString({Languages.DE: self.simple_string_de, Languages.FR: self.simple_string_fr})
        for tmp in ls:
            if tmp[0] == Languages.DE:
                self.assertEqual(tmp[1], self.simple_string_de)
            elif tmp[0] == Languages.FR:
                self.assertEqual(tmp[1], self.simple_string_fr)


if __name__ == "__main__":
    pytest.main([__file__])
