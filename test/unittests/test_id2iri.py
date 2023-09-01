# pylint: disable=missing-class-docstring,missing-function-docstring

import shutil
import unittest
from pathlib import Path

import pytest
import regex

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.id2iri import id2iri
from dsp_tools.utils.shared import get_most_recent_glob_match


class TestIdToIri(unittest.TestCase):
    tmp_dir = Path("testdata/tmp")

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        cls.tmp_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree(cls.tmp_dir)

    def test_invalid_xml_file_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"File test\.xml could not be found"):
            id2iri(
                xml_file="test.xml",
                json_file="testdata/id2iri/test-id2iri-mapping.json",
            )

    def test_invalid_json_file_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"File test\.json could not be found"):
            id2iri(
                xml_file="testdata/id2iri/test-id2iri-data.xml",
                json_file="test.json",
            )

    def test_replace_id_with_iri(self) -> None:
        """Check that the correct IRIs appear in the correct order in the output file"""
        id2iri(
            xml_file="testdata/id2iri/test-id2iri-data.xml",
            json_file="testdata/id2iri/test-id2iri-mapping.json",
        )
        out_file = get_most_recent_glob_match("test-id2iri-data_replaced_*.xml")
        with open(out_file, encoding="utf-8", mode="r") as file:
            out_file_content = file.read()
        out_file.unlink()
        iris = regex.findall(r"http://rdfh\.ch/082E/\w+", out_file_content)
        iris_expected = [
            "http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
            "http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
        ]
        self.assertListEqual(iris, iris_expected)


if __name__ == "__main__":
    pytest.main([__file__])
