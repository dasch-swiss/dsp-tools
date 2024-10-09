import pickle
from pathlib import Path

from lxml import etree

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _save_upload_state


def test_save_upload_state(tmp_path: Path) -> None:
    resource_str = """
    <resource label="Annotation to TestthingOhnePermissions" id="annotation_1" restype="foo:bar">
        <text-prop name="hasComment">
            <text encoding="xml" permissions="open">This is an annotation to TestthingOhnePermissions.</text>
        </text-prop>
    </resource>
    """
    save_location = tmp_path / "upload_state.pkl"
    config = UploadConfig(diagnostics=DiagnosticsConfig(save_location=save_location))
    upload_state = UploadState(
        pending_resources=[XMLResource.from_node(etree.fromstring(resource_str), default_ontology="test")],
        failed_uploads=[],
        iri_resolver=IriResolver({"foo": "bar"}),
        pending_stash=None,
        config=config,
        permissions_lookup={},
    )
    msg = _save_upload_state(upload_state)
    with open(save_location, "rb") as f:
        saved_state: UploadState = pickle.load(f)  # noqa: S301 (deserialization of untrusted data)
    assert msg == f"Saved the current upload state to {save_location}.\n"
    assert len(upload_state.pending_resources) == len(saved_state.pending_resources)
    assert [r.res_id for r in upload_state.pending_resources] == [r.res_id for r in saved_state.pending_resources]
    assert upload_state.iri_resolver.lookup == saved_state.iri_resolver.lookup
    assert upload_state.pending_stash == saved_state.pending_stash
    assert upload_state.config == saved_state.config
    assert upload_state.permissions_lookup == saved_state.permissions_lookup
