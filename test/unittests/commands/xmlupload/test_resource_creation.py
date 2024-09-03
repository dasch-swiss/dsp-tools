from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _tidy_up_resource_creation_idempotent


def test_idempotency_on_success() -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_1 text</text></text-prop>
        </resource>
        """,
        """
        <resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id">
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_2 text</text></text-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources.copy(), None, UploadConfig(), {})
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, "foo_1_iri", xml_resources[0])
        assert upload_state.pending_resources == xml_resources[1:]
        assert upload_state.failed_uploads == []
        assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri"}
        assert not upload_state.pending_stash


def test_idempotency_on_failure() -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_1 text</text></text-prop>
        </resource>
        """,
        """
        <resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id">
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_2 text</text></text-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources.copy(), None, UploadConfig(), {})
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, None, xml_resources[0])
        assert upload_state.pending_resources == xml_resources[1:]
        assert upload_state.failed_uploads == ["foo_1_id"]
        assert upload_state.iri_resolver.lookup == {}
        assert not upload_state.pending_stash
