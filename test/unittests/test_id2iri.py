# pylint: disable=missing-class-docstring,missing-function-docstring

import shutil
import unittest
from pathlib import Path

import pytest
from lxml import etree

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
        """Check that the IRIs appear at the correct place in the output file"""
        id2iri(
            xml_file="testdata/id2iri/test-id2iri-data.xml",
            json_file="testdata/id2iri/test-id2iri-mapping.json",
        )
        out_file = get_most_recent_glob_match("test-id2iri-data_replaced_*.xml")
        root = etree.parse(out_file).getroot()
        out_file.unlink()
        resources = root.getchildren()
        iris = [
            resources[1].getchildren()[2].getchildren()[0].text,
            resources[1].getchildren()[2].getchildren()[1].text,
            resources[2].getchildren()[1].getchildren()[0][0].attrib["href"],
            resources[2].getchildren()[1].getchildren()[0][1][0][0].attrib["href"],
            resources[2].getchildren()[1].getchildren()[0][2].attrib["href"],
            resources[3].getchildren()[1].getchildren()[0][0].attrib["href"],
            resources[3].getchildren()[1].getchildren()[0][1][0][0].attrib["href"],
            resources[3].getchildren()[1].getchildren()[0][2].attrib["href"],
            resources[3].getchildren()[2].getchildren()[0].text,
            resources[3].getchildren()[2].getchildren()[1].text,
        ]
        iris_expected = [
            "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss",
            "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss",
        ]
        self.assertListEqual(iris, iris_expected)

    def test_id2iri_remove_resources(self) -> None:
        """
        Check that the IRIs appear at the correct place in the output file,
        and that all resources are deleted where no replacement had taken place.
        """
        id2iri(
            xml_file="testdata/id2iri/remove-resources/data.xml",
            json_file="testdata/id2iri/remove-resources/mapping.json",
            remove_resource_if_id_in_mapping=True,
        )
        out_file = get_most_recent_glob_match("data_replaced_*.xml")
        root = etree.parse(out_file).getroot()
        out_file.unlink()
        resources = root.getchildren()
        iris = [
            resources[0].getchildren()[1].getchildren()[0].text,
            resources[0].getchildren()[1].getchildren()[1].text,
            resources[1].getchildren()[0].getchildren()[0][0].attrib["href"],
            resources[1].getchildren()[1].getchildren()[0].text,
        ]
        iris_expected = [
            "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
        ]
        self.assertListEqual(iris, iris_expected)

        all_resource_labels = [r.attrib["label"] for r in resources]
        self.assertListEqual(all_resource_labels, ["resptr_only", "resptr_and_salsah_link"])


if __name__ == "__main__":
    pytest.main([__file__])
