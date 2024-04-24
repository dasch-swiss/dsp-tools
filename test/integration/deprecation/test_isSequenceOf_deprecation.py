import warnings

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file


def test_xmlupload() -> None:
    with warnings.catch_warnings(record=True) as captured_warnings:
        xml = etree.fromstring(
            """ 
            <knora xmlns="https://dasch.swiss/schema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="https://dasch.swiss/schema ../../src/dsp_tools/resources/schema/data.xsd"
                shortcode="4123"
                default-ontology="testonto">
                <resource label="foo_1" restype=":foo" id="foo_1">
                    <text-prop name=":hasSimpleText">
                        <text encoding="utf8">Sequence of a Video Resource</text>
                    </text-prop>
                    <resptr-prop name="isSequenceOf">
                        <resptr>bar_1</resptr>
                    </resptr-prop>
                    <interval-prop name="hasSequenceBounds">
                        <interval>-10.0:-5.1</interval>
                    </interval-prop>
                </resource>
                <resource label="bar_1" restype=":bar" id="bar_1" />
            </knora>
            """
        ).getroottree()
        validate_and_parse_xml_file(imgdir=".", input_file=xml, preprocessing_done=False)
    expected_warning = "Support for the following properties will be removed soon: isSequenceOf, hasSequenceBounds"
    assert any(regex.search(expected_warning, x) for x in [str(x.message) for x in captured_warnings])
