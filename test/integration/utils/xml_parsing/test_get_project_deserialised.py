import pytest
from lxml import etree

from dsp_tools.utils.xml_parsing.get_project_deserialised import get_project_deserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ProjectDeserialised


def test_to_data_rdf(data_xml: etree._Element) -> None:
    res = get_project_deserialised(data_xml)
    assert isinstance(res, ProjectDeserialised)
    assert res.info.shortcode == "9999"
    assert res.info.default_onto == "onto"
    assert len(res.data.resources) == 18


if __name__ == "__main__":
    pytest.main([__file__])
