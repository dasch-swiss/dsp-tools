# pylint: disable=missing-class-docstring,missing-function-docstring

from pathlib import Path
import shutil
import unittest

import pytest

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.id_to_iri import id_to_iri
from dsp_tools.utils.xml_upload import _parse_xml_file


class TestIdToIri(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        Path("testdata/tmp").mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree("testdata/tmp")

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
        out_file = list(Path("testdata/tmp").glob("test-id2iri-data_replaced_*.xml"))[0]
        out_file_parsed = _parse_xml_file(out_file)
        resptr_props = out_file_parsed.xpath("/knora/resource/resptr-prop/resptr")
        resptr_props_contents = [r.text for r in resptr_props]
        self.assertEqual(
            resptr_props_contents,
            ["http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg", "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ"],
        )


if __name__ == "__main__":
    pytest.main([__file__])
