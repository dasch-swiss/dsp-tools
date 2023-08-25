# pylint: disable=missing-class-docstring,missing-function-docstring

from pathlib import Path
import shutil
import unittest

import pytest
import regex

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.id_to_iri import id_to_iri
from dsp_tools.utils.xml_upload import parse_xml_file


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
            id_to_iri(
                xml_file="test.xml",
                json_file="testdata/id2iri/test-id2iri-mapping.json",
            )

    def test_invalid_json_file_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"File test\.json could not be found"):
            id_to_iri(
                xml_file="testdata/id2iri/test-id2iri-data.xml",
                json_file="test.json",
            )

    def test_replace_id_with_iri(self) -> None:
        id_to_iri(
            xml_file="testdata/id2iri/test-id2iri-data.xml",
            json_file="testdata/id2iri/test-id2iri-mapping.json",
        )
        out_file = list(Path(".").glob("test-id2iri-data_replaced_*.xml"))[0]
        out_file_parsed = parse_xml_file(out_file)
        out_file.unlink()

        resptr_props = [x.text for x in out_file_parsed.xpath("/knora/resource/resptr-prop/resptr")]
        resptr_props_expected = [
            "http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
            "http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
        ]
        self.assertEqual(resptr_props, resptr_props_expected)

        salsah_links = [x.attrib.get("href", "") for x in out_file_parsed.xpath("/knora/resource/text-prop/text//a")]
        salsah_links = [regex.sub("IRI:|:IRI", "", x) for x in salsah_links]
        salsah_links_expected = [
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
            "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
            "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
            "http://rdfh.ch/082E/qwasddoiu876flkjh67dss",
        ]
        self.assertEqual(salsah_links, salsah_links_expected)


if __name__ == "__main__":
    pytest.main([__file__])
