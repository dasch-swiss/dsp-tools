import pickle
from pathlib import Path

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _save_upload_state


def test_save_upload_state(tmp_path: Path) -> None:
    save_location = tmp_path / "upload_state.pkl"
    config = UploadConfig(diagnostics=DiagnosticsConfig(save_location=save_location))
    upload_state = UploadState(
        pending_resources=[
            ProcessedResource("id", "type", "label", None, [ProcessedSimpleText("Some text", "prop", None, None)])
        ],
        failed_uploads=[],
        iri_resolver=IriResolver({"foo": "bar"}),
        pending_stash=None,
        config=config,
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
