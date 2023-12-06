import shutil
import unittest
from pathlib import Path
from typing import ClassVar

import pytest
import regex
from lxml import etree

from dsp_tools.commands.id2iri import _remove_resources_if_id_in_mapping, _replace_ids_by_iris, id2iri
from dsp_tools.models.exceptions import BaseError


class TestIdToIri(unittest.TestCase):
    tmp_dir = Path("testdata/tmp")
    mapping: ClassVar = {
        "test_thing_0": "http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg",
        "test_thing_1": "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ",
        "test_thing_2": "http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak",
        "test_thing_with_ark_1": "http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss",
    }

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

    def test_replace_ids_by_iris_no_replacements(self) -> None:
        xml = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="no_replacements" restype=":TestThing" id="no_replacements">
                <text-prop name=":hasRichtext">
                    <text encoding="xml"><a class="salsa-link" href="IRI:id_that_is_not_in_mapping:IRI">link</a></text>
                </text-prop>
            </resource>
        </knora>
        """
        xml = regex.sub(r"^(\n +)|(\n +)$", "", xml)
        root_replaced = _replace_ids_by_iris(etree.fromstring(xml), self.mapping)
        xml_replaced = etree.tostring(root_replaced).decode("utf-8")
        self.assertEqual(xml_replaced, xml)

    def test_replace_ids_by_iris_resptr_only(self) -> None:
        xml = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="resptr_only" restype=":TestThing" id="resptr_only">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">Text</text>
                </text-prop>
                <resptr-prop name=":hasTestThing2">
                    <resptr>test_thing_0</resptr>
                    <resptr>test_thing_with_ark_1</resptr>
                </resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="resptr_only" restype=":TestThing" id="resptr_only">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">Text</text>
                </text-prop>
                <resptr-prop name=":hasTestThing2">
                    <resptr>http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg</resptr>
                    <resptr>http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss</resptr>
                </resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = regex.sub(r"^(\n +)|(\n +)$", "", xml_expected)
        root_replaced = _replace_ids_by_iris(etree.fromstring(xml), self.mapping)
        xml_replaced = etree.tostring(root_replaced).decode("utf-8")
        self.assertEqual(xml_replaced, xml_expected)

    def test_replace_ids_by_iris_salsah_link_only(self) -> None:
        xml = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="salsah_link_only" restype=":TestThing" id="salsah_link_only">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">
                        Text with a <a class="salsah-link" href="IRI:test_thing_1:IRI">
                        link to test_thing_1</a> and <strong>a bold <em>and italicized
                        <a class="salsah-link" href="IRI:test_thing_2:IRI">
                        link to test_thing_2</a></em></strong>and a 
                        <a class="salsah-link" href="IRI:test_thing_with_ark_1:IRI">link</a> 
                    </text>
                </text-prop>
            </resource>
        </knora>
        """
        xml_expected = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="salsah_link_only" restype=":TestThing" id="salsah_link_only">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">
                        Text with a <a class="salsah-link" href="http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ">
                        link to test_thing_1</a> and <strong>a bold <em>and italicized
                        <a class="salsah-link" href="http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak">
                        link to test_thing_2</a></em></strong>and a 
                        <a class="salsah-link" href="http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss">link</a> 
                    </text>
                </text-prop>
            </resource>
        </knora>
        """
        xml_expected = regex.sub(r"^(\n +)|(\n +)$", "", xml_expected)
        root_replaced = _replace_ids_by_iris(etree.fromstring(xml), self.mapping)
        xml_replaced = etree.tostring(root_replaced).decode("utf-8")
        self.assertEqual(xml_replaced, xml_expected)

    def test_replace_ids_by_iris_resptr_and_salsah_link(self) -> None:
        xml = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="resptr_and_salsah_link" restype=":TestThing" id="resptr_and_salsah_link">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">
                        Text with a <a class="salsah-link" href="IRI:test_thing_1:IRI">
                        link to test_thing_1</a> and <strong>a bold <em>and italicized
                        <a class="salsah-link" href="IRI:test_thing_2:IRI">
                        link to test_thing_2</a></em></strong>and a 
                        <a class="salsah-link" href="IRI:test_thing_with_ark_1:IRI">link</a> 
                    </text>
                </text-prop>
                <resptr-prop name=":hasTestThing2">
                    <resptr>test_thing_0</resptr>
                    <resptr>test_thing_with_ark_1</resptr>
                </resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="resptr_and_salsah_link" restype=":TestThing" id="resptr_and_salsah_link">
                <text-prop name=":hasRichtext">
                    <text encoding="xml">
                        Text with a <a class="salsah-link" href="http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ">
                        link to test_thing_1</a> and <strong>a bold <em>and italicized
                        <a class="salsah-link" href="http://rdfh.ch/082E/1l63Oasdfopiujlkmn78ak">
                        link to test_thing_2</a></em></strong>and a 
                        <a class="salsah-link" href="http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss">link</a> 
                    </text>
                </text-prop>
                <resptr-prop name=":hasTestThing2">
                    <resptr>http://rdfh.ch/082E/-lRvrg7tQI6aVpcTJbVrwg</resptr>
                    <resptr>http://rdfh.ch/082E/qwasddoiu8_6flkjh67dss</resptr>
                </resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = regex.sub(r"^(\n +)|(\n +)$", "", xml_expected)
        root_replaced = _replace_ids_by_iris(etree.fromstring(xml), self.mapping)
        xml_replaced = etree.tostring(root_replaced).decode("utf-8")
        self.assertEqual(xml_replaced, xml_expected)

    def test_id2iri_remove_resources(self) -> None:
        xml = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="test_thing_0" restype=":TestThing" id="test_thing_0">
                <text-prop name=":hasRichtext"><text encoding="xml">Hello world</text></text-prop>
            </resource>
            <resource label="id_that_is_not_in_mapping" restype=":TestThing" id="id_that_is_not_in_mapping">
                <resptr-prop name=":foo"><resptr>test_thing_0</resptr></resptr-prop>
            </resource>
            <resource label="test_thing_1" restype=":TestThing" id="test_thing_1">
                <resptr-prop name=":foo"><resptr>test_thing_0</resptr></resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = """
        <knora shortcode="4123" default-ontology="testonto">
            <resource label="id_that_is_not_in_mapping" restype=":TestThing" id="id_that_is_not_in_mapping">
                <resptr-prop name=":foo"><resptr>test_thing_0</resptr></resptr-prop>
            </resource>
        </knora>
        """
        xml_expected = xml_expected.replace("\n", "").replace(" ", "")
        tree_returned = _remove_resources_if_id_in_mapping(
            tree=etree.fromstring(xml),
            mapping=self.mapping,
        )
        xml_returned = etree.tostring(tree_returned, pretty_print=False).decode("utf-8")
        xml_returned = xml_returned.replace("\n", "").replace(" ", "")
        self.assertEqual(xml_returned, xml_expected)


if __name__ == "__main__":
    pytest.main([__file__])
