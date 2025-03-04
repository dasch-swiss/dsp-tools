import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import _check_for_duplicate_bitstreams
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import _check_if_resptr_targets_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import _check_if_salsah_targets_exist
from dsp_tools.models.custom_warnings import DspToolsUserWarning


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


def test_check_for_duplicate_bitstreams() -> None:
    xml = """
    <knora>
        <resource id="res_1"></resource>
        <resource id="res_2"><bitstream>path/to/file4.txt</bitstream></resource>
        <resource id="res_3"><bitstream>path/to/file1.txt</bitstream></resource>
        <resource id="res_4"><bitstream>path/to/file2.txt</bitstream></resource>
        <resource id="res_5"><bitstream>path/to/file1.txt</bitstream></resource>
        <resource id="res_6"><bitstream>path/to/file3.txt</bitstream></resource>
        <resource id="res_7"><bitstream>path/to/file1.txt</bitstream></resource>
        <resource id="res_8"><bitstream>path/to/file3.txt</bitstream></resource>
        <resource id="res_9"><bitstream>path/to/file4.txt</bitstream></resource>
        <resource id="res_10"><bitstream>path/to/file4.txt</bitstream></resource>
        <resource id="res_11"><bitstream>path/to/file4.txt</bitstream></resource>
        <resource id="res_12"><bitstream>path/to/file4.txt</bitstream></resource>
  </knora>
    """
    expected = (
        r"Your XML file contains duplicate bitstreams\. "
        r"This means that the same file will be uploaded multiple times to DSP, each time creating a new resource\. "
        r"Please check if it is possible to create only 1 resource per multimedia file\. "
        r"\n\nThe following duplicates were found: "
        r"\n - 5 times: path/to/file4\.txt"
        r"\n - 3 times: path/to/file1\.txt"
        r"\n - 2 times: path/to/file3\.txt"
    )
    root = etree.fromstring(xml)
    with pytest.warns(DspToolsUserWarning, match=expected):
        _check_for_duplicate_bitstreams(root, ".")


if __name__ == "__main__":
    pytest.main([__file__])
