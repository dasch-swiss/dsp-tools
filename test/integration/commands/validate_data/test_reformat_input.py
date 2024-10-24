import pytest
from lxml import etree

from dsp_tools.commands.validate_data.deserialise_input import deserialise_xml
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectDeserialised


def test_to_data_rdf(data_xml: etree._Element) -> None:
    res = deserialise_xml(data_xml)
    assert isinstance(res, ProjectDeserialised)
    assert res.info.shortcode == "9999"
    assert res.info.default_onto == "onto"
    assert len(res.data.resources) == 17


if __name__ == "__main__":
    pytest.main([__file__])
