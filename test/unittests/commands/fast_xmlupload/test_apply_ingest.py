from lxml import etree

from dsp_tools.commands.fast_xmlupload.apply_ingest import replace_bitstream_paths

# pylint: disable=missing-class-docstring,missing-function-docstring


class TestReplaceBitstreamPaths:
    def test_all_good(self) -> None:
        xml = (
            '<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            'permissions="res-default"><bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource></knora>"
        )
        root = etree.fromstring(xml)
        reference_dict = {"images/Fluffy.jpg": "fluffy_uuid"}
        res_tree, res_msg = replace_bitstream_paths(root, reference_dict)  # type: ignore[arg-type]
        assert not res_msg.media_no_uuid
        assert not res_msg.unused_media_paths
        expected = (
            b'<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            b'permissions="res-default"><bitstream permissions="prop-default">fluffy_uuid</bitstream>'
            b"</resource></knora>"
        )
        assert etree.tostring(res_tree) == expected

    def test_extra_paths(self) -> None:
        xml = (
            '<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            'permissions="res-default"><bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource></knora>"
        )
        root = etree.fromstring(xml)
        reference_dict = {"images/Fluffy.jpg": "fluffy_uuid", "extra_media": "extra_uuid"}
        res_tree, res_msg = replace_bitstream_paths(root, reference_dict)  # type: ignore[arg-type]
        assert not res_msg.media_no_uuid
        assert res_msg.unused_media_paths == ["extra_media"]
        expected = (
            b'<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            b'permissions="res-default"><bitstream permissions="prop-default">fluffy_uuid</bitstream>'
            b"</resource></knora>"
        )
        assert etree.tostring(res_tree) == expected

    def test_missing_paths(self) -> None:
        xml = (
            '<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            'permissions="res-default"><bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            "</resource></knora>"
        )
        root = etree.fromstring(xml)
        reference_dict = {"extra_media": "extra_uuid"}
        res_tree, res_msg = replace_bitstream_paths(root, reference_dict)  # type: ignore[arg-type]
        assert res_msg.media_no_uuid == [("Fluffy1", "images/Fluffy.jpg")]
        assert res_msg.unused_media_paths == ["extra_media"]
        expected = (
            b'<knora><resource label="Fluffy Image" restype=":Image2D" id="Fluffy1" '
            b'permissions="res-default"><bitstream permissions="prop-default">images/Fluffy.jpg</bitstream>'
            b"</resource></knora>"
        )
        assert etree.tostring(res_tree) == expected
