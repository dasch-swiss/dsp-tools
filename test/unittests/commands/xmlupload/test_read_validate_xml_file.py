import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.read_validate_xml_file import _check_if_resptr_targets_exist
from dsp_tools.commands.xmlupload.read_validate_xml_file import _check_if_salsah_targets_exist


def test_check_if_resptr_targets_exist() -> None:
    """Check correct input"""
    xml = """
    <knora>
        <resource id="resource1">
            <resptr-prop name="resptr1"><resptr>resource2</resptr></resptr-prop>
        </resource>
        <resource id="resource2">
            <resptr-prop name="resptr2"><resptr>resource1</resptr></resptr-prop>
        </resource>
    </knora>
    """
    root = etree.fromstring(xml)
    errors_returned = _check_if_resptr_targets_exist(root)
    assert not errors_returned


def test_check_if_resptr_targets_exist_invalid() -> None:
    """Check invalid input"""
    xml = """
    <knora>
        <resource id="resource1">
            <resptr-prop name="resptr1"><resptr>resource3</resptr></resptr-prop>
        </resource>
        <resource id="resource2">
            <resptr-prop name="resptr2"><resptr>resource4</resptr></resptr-prop>
        </resource>
    </knora>
    """
    root = etree.fromstring(xml)
    errors_returned = _check_if_resptr_targets_exist(root)
    errors_expected = [
        "Resource 'resource1', property 'resptr1' has an invalid link target 'resource3'",
        "Resource 'resource2', property 'resptr2' has an invalid link target 'resource4'",
    ]
    assert errors_returned == errors_expected


def test_check_if_salsah_targets_exist() -> None:
    """Check correct input"""
    xml = """
    <knora>
        <resource id="resource1">
            <text-prop name="text1">
                <text encoding="xml">
                    <a class="salsah-link" href="IRI:resource2:IRI">resource2</a>
                </text>
            </text-prop>
        </resource>
        <resource id="resource2">
            <text-prop name="text2">
                <text encoding="xml">
                    <a class="salsah-link" href="IRI:resource1:IRI">resource1</a>
                </text>
            </text-prop>
        </resource>
    </knora>
    """
    root = etree.fromstring(xml)
    errors_returned = _check_if_salsah_targets_exist(root)
    assert not errors_returned


def test_check_if_salsah_targets_exist_invalid() -> None:
    """Check invalid input"""
    xml = """
    <knora>
        <resource id="resource1">
            <text-prop name="text1">
                <text encoding="xml">
                    <a class="salsah-link" href="IRI:resource3:IRI">resource3</a>
                </text>
            </text-prop>
        </resource>
        <resource id="resource2">
            <text-prop name="text2">
                <text encoding="xml">
                    <a class="salsah-link" href="IRI:resource4:IRI">resource4</a>
                </text>
            </text-prop>
        </resource>
    </knora>
    """
    root = etree.fromstring(xml)
    errors_returned = _check_if_salsah_targets_exist(root)
    errors_expected = [
        "Resource 'resource1', property 'text1' has an invalid link target 'IRI:resource3:IRI'",
        "Resource 'resource2', property 'text2' has an invalid link target 'IRI:resource4:IRI'",
    ]
    assert errors_returned == errors_expected


if __name__ == "__main__":
    pytest.main([__file__])
