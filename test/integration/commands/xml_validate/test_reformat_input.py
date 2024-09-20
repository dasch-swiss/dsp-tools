import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.reformat_input import to_data_rdf


def test_to_data_rdf(data_xml: etree._Element) -> None:
    res = to_data_rdf(data_xml)
    assert isinstance(res, DataRDF)
    assert res.shortcode == "9999"
    assert res.default_onto == "onto"
    assert len(res.resources) == 14


if __name__ == "__main__":
    pytest.main([__file__])
