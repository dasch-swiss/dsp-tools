import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.deserialise_input import deserialise_xml
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDataDeserialised


def test_to_data_rdf(data_xml: etree._Element) -> None:
    res = deserialise_xml(data_xml)
    assert isinstance(res, ProjectDataDeserialised)
    assert res.shortcode == "9999"
    assert res.default_onto == "onto"
    assert len(res.resources) == 14


if __name__ == "__main__":
    pytest.main([__file__])
