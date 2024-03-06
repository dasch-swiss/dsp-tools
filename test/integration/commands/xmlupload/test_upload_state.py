import pickle
from pathlib import Path

from lxml import etree

from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _save_upload_state


def test_save_upload_state(tmp_path: Path) -> None:
    resource_str = """
    <resource label="Annotation to TestthingOhnePermissions" id="annotation_1" restype="foo:bar">
        <text-prop name="hasComment">
            <text encoding="xml" permissions="prop-default">This is an annotation to TestthingOhnePermissions.</text>
        </text-prop>
    </resource>
    """
    save_location = tmp_path / "upload_state.pkl"
    config = UploadConfig(diagnostics=DiagnosticsConfig(save_location=save_location))
    upload_state = UploadState(
        pending_resources=[XMLResource(etree.fromstring(resource_str), default_ontology="test")],
        iri_resolver_lookup={"foo": "bar"},
        stash=None,
        config=config,
    )
    _save_upload_state(upload_state)
    with open(save_location, "rb") as f:
        saved_state = pickle.load(f)  # noqa: S301 (deserialization of untrusted data)
    assert upload_state.iri_resolver_lookup == saved_state.iri_resolver_lookup
    assert upload_state.config == saved_state.config
    assert upload_state.stash == saved_state.stash
    assert len(upload_state.pending_resources) == len(saved_state.pending_resources)
    assert [r.res_id for r in upload_state.pending_resources] == [r.res_id for r in saved_state.pending_resources]
