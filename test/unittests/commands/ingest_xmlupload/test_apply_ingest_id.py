from lxml import etree

from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import replace_filepath_with_sipi_id

# pylint: disable=missing-class-docstring,missing-function-docstring


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
        res_tree, res_msg = replace_filepath_with_sipi_id(root, reference_dict)
        assert not res_msg.media_no_id
        assert not res_msg.unused_media_paths
        expected = (
            b"<knora>"
            b'<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            b'<bitstream permissions="prop-default">fluffy_id</bitstream>'
            b"</resource></knora>"
        )
        assert etree.tostring(res_tree) == expected

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
        res_tree, res_msg = replace_filepath_with_sipi_id(root, reference_dict)
        assert not res_msg.media_no_id
        assert res_msg.unused_media_paths == ["extra_media"]
        expected = (
            b"<knora>"
            b'<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            b'<bitstream permissions="prop-default">fluffy_id</bitstream>'
            b"</resource>"
            b"</knora>"
        )
        assert etree.tostring(res_tree) == expected

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
        res_tree, res_msg = replace_filepath_with_sipi_id(root, reference_dict)
        assert res_msg.media_no_id == [("Fluffy1", "images/Fluffy.jpg")]
        assert res_msg.unused_media_paths == ["extra_media"]
        expected = (
            b"<knora>"
            b'<resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" permissions="res-default">'
            b'<bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            b"</resource>"
            b"</knora>"
        )
        assert etree.tostring(res_tree) == expected
