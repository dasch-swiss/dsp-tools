from lxml import etree

from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import replace_filepath_with_sipi_id


class TestReplaceBitstreamPaths:
    def test_all_good(self) -> None:
        xml = (
            "<knora>"
            '<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            '<bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource>"
            "</knora>"
        )
        root = etree.ElementTree(etree.fromstring(xml))
        reference_dict = {"images/Fluffy.jpg": "fluffy_id"}
        res_tree, ingest_info = replace_filepath_with_sipi_id(root, reference_dict)
        assert not ingest_info.media_no_id
        assert not ingest_info.unused_media_paths
        res_bitstream = res_tree.getroot()[0][0]
        assert res_bitstream.text == "fluffy_id"
        assert res_bitstream.attrib["permissions"] == "prop-default"
        assert res_bitstream.tag == "bitstream"

    def test_extra_paths(self) -> None:
        xml = (
            "<knora>"
            '<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            '<bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource>"
            "</knora>"
        )
        root = etree.ElementTree(etree.fromstring(xml))
        reference_dict = {"images/Fluffy.jpg": "fluffy_id", "extra_media": "extra_id"}
        res_tree, ingest_info = replace_filepath_with_sipi_id(root, reference_dict)
        assert not ingest_info.media_no_id
        assert ingest_info.unused_media_paths == ["extra_media"]
        res_bitstream = res_tree.getroot()[0][0]
        assert res_bitstream.text == "fluffy_id"
        assert res_bitstream.attrib["permissions"] == "prop-default"
        assert res_bitstream.tag == "bitstream"

    def test_missing_paths(self) -> None:
        xml = (
            "<knora>"
            '<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            '<bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource>"
            "</knora>"
        )
        root = etree.ElementTree(etree.fromstring(xml))
        reference_dict = {"extra_media": "extra_id"}
        res_tree, ingest_info = replace_filepath_with_sipi_id(root, reference_dict)
        assert ingest_info.media_no_id == [("Fluffy1", "images/Fluffy.jpg")]
        assert ingest_info.unused_media_paths == ["extra_media"]
        res_bitstream = res_tree.getroot()[0][0]
        assert res_bitstream.text == "images/Fluffy.jpg"
        assert res_bitstream.attrib["permissions"] == "prop-default"
        assert res_bitstream.tag == "bitstream"
