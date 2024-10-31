import pytest
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import replace_filepath_with_internal_filename


class TestReplaceBitstreamPaths:
    def test_all_good(self) -> None:
        xml = """
        <knora>
            <resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="open">
                <bitstream permissions="open">images/Fluffy.jpg</bitstream>
            </resource>
        </knora>
        """
        root = etree.ElementTree(etree.fromstring(xml)).getroot()
        reference_dict = {"images/Fluffy.jpg": "fluffy_id"}
        res_root, ingest_info = replace_filepath_with_internal_filename(root, reference_dict)
        assert not ingest_info.mediafiles_no_id
        assert not ingest_info.unused_mediafiles
        res_bitstream = res_root[0][0]
        assert res_bitstream.text == "fluffy_id"
        assert res_bitstream.attrib["permissions"] == "open"
        assert res_bitstream.tag == "bitstream"

    def test_extra_paths(self) -> None:
        xml = """
        <knora>
            <resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="open">
                <bitstream permissions="open">images/Fluffy.jpg</bitstream>
            </resource>
        </knora>
        """
        root = etree.ElementTree(etree.fromstring(xml)).getroot()
        reference_dict = {"images/Fluffy.jpg": "fluffy_id", "extra_media": "extra_id"}
        res_root, ingest_info = replace_filepath_with_internal_filename(root, reference_dict)
        assert not ingest_info.mediafiles_no_id
        assert ingest_info.unused_mediafiles == ["extra_media"]
        res_bitstream = res_root[0][0]
        assert res_bitstream.text == "fluffy_id"
        assert res_bitstream.attrib["permissions"] == "open"
        assert res_bitstream.tag == "bitstream"

    def test_missing_paths(self) -> None:
        xml = """
        <knora>
            <resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="open">
                <bitstream permissions="open">images/Fluffy.jpg</bitstream>
            </resource>
        </knora>
        """
        root = etree.ElementTree(etree.fromstring(xml)).getroot()
        reference_dict = {"extra_media": "extra_id"}
        res_root, ingest_info = replace_filepath_with_internal_filename(root, reference_dict)
        assert ingest_info.mediafiles_no_id == [("Fluffy1", "images/Fluffy.jpg")]
        assert ingest_info.unused_mediafiles == ["extra_media"]
        res_bitstream = res_root[0][0]
        assert res_bitstream.text == "images/Fluffy.jpg"
        assert res_bitstream.attrib["permissions"] == "open"
        assert res_bitstream.tag == "bitstream"


if __name__ == "__main__":
    pytest.main([__file__])
