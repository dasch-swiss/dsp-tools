import pytest
from lxml import etree

from dsp_tools.utils.xml_parsing.get_data_deserialised import get_data_deserialised


def test_to_data_rdf(data_xml: etree._Element) -> None:
    shortcode, data = get_data_deserialised(data_xml)
    assert shortcode == "9999"
    assert len(data.resources) == 18


if __name__ == "__main__":
    pytest.main([__file__])
