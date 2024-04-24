import pytest
import regex
from lxml import etree

from dsp_tools.commands.project.create.project_validate import validate_project
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file
from dsp_tools.models.custom_warnings import DspToolsFutureWarning


def test_create() -> None:
    data_model = {
        "$schema": "../../src/dsp_tools/resources/schema/project.json",
        "project": {
            "shortcode": "4123",
            "shortname": "systematic-tp",
            "longname": "systematic test project",
            "descriptions": {
                "en": "A systematic test project",
            },
            "keywords": ["testing"],
            "ontologies": [
                {
                    "name": "testonto",
                    "label": "Test ontology",
                    "comment": "This is the main ontology of this project. Further down, another one is defined.",
                    "properties": [
                        {
                            "name": "hasBounds",
                            "super": ["hasSequenceBounds"],
                            "object": "IntervalValue",
                            "labels": {"en": "Interval defining the start and end point of the sequence"},
                            "gui_element": "Interval",
                        },
                    ],
                    "resources": [
                        {
                            "name": "resource1",
                            "super": "Resource",
                            "labels": {"en": "resource1"},
                            "cardinalities": [{"propname": ":hasBounds", "cardinality": "1"}],
                        }
                    ],
                },
            ],
        },
    }

    rgx = regex.escape("Support for the following properties will be removed soon: isSequenceOf, hasSequenceBounds")
    with pytest.warns(DspToolsFutureWarning, match=rgx):
        validate_project(data_model, False)


def test_xmlupload() -> None:
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
    rgx = regex.escape("Support for the following properties will be removed soon: isSequenceOf, hasSequenceBounds")
    with pytest.warns(DspToolsFutureWarning, match=rgx):
        validate_and_parse_xml_file(imgdir=".", input_file=xml, preprocessing_done=False)
