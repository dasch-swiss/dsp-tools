import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.data_deserialised import DataDeserialised
from dsp_tools.commands.xml_validate.reformat_input import transform_into_project_deserialised


def test_transform_into_project_deserialised(data_xml: etree._Element) -> None:
    res = transform_into_project_deserialised(data_xml)
    assert isinstance(res, DataDeserialised)
    assert res.shortcode == "9999"
    assert res.default_onto == "onto"
    assert len(res.resources) == 14


if __name__ == "__main__":
    pytest.main([__file__])
