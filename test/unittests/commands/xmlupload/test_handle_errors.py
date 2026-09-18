from pathlib import Path

import pytest
from requests import ReadTimeout

from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt_during_creation
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_connection_error
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_timeout
from dsp_tools.commands.xmlupload.handle_errors import interruption_is_indicated
from dsp_tools.commands.xmlupload.handle_errors import persist_state_for_resume
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import PermanentConnectionError


def _make_upload_state(save_location: Path, interrupt_after: int | None = None) -> UploadState:
    config = UploadConfig(
        interrupt_after=interrupt_after,
        diagnostics=DiagnosticsConfig(save_location=save_location),
    )
    return UploadState(
        pending_resources=[],
        pending_stash=None,
        config=config,
        failed_uploads=[],
        iri_resolver=IriResolver({"foo_id": "http://rdfh.ch/0000/foo_iri"}),
    )


class TestKeyboardInterrupt:
    def test_raises_keyboard_interrupt(self) -> None:
        with pytest.raises(KeyboardInterrupt):
            with pytest.warns(DspToolsUserWarning, match="manually interrupted"):
                handle_keyboard_interrupt()

    def test_during_creation_raises_keyboard_interrupt(self) -> None:
        with pytest.raises(KeyboardInterrupt, match="skip-first-resource"):
            with pytest.warns(DspToolsUserWarning, match="skip-first-resource"):
                handle_keyboard_interrupt_during_creation("foo_id")


class TestFailureInterruptions:
    def test_permanent_timeout(self) -> None:
        with pytest.raises(XmlUploadInterruptedError, match="skip-first-resource"):
            with pytest.warns(DspToolsUserWarning, match="ReadTimeout"):
                handle_permanent_timeout(ReadTimeout(), "foo_id")

    def test_permanent_connection_error(self) -> None:
        with pytest.raises(XmlUploadInterruptedError, match="Lost connection to DSP server"):
            handle_permanent_connection_error(PermanentConnectionError("server is down"))


class TestInterruptionIsIndicated:
    def test_not_configured(self) -> None:
        upload_state = _make_upload_state(Path("latest.pkl"), interrupt_after=None)
        assert not interruption_is_indicated(upload_state, 0)
        assert not interruption_is_indicated(upload_state, 1000)

    def test_configured(self) -> None:
        upload_state = _make_upload_state(Path("latest.pkl"), interrupt_after=2)
        assert not interruption_is_indicated(upload_state, 0)
        assert interruption_is_indicated(upload_state, 1)
        assert interruption_is_indicated(upload_state, 2)


class TestPersistStateForResume:
    def test_saves_pickle_and_informs_user(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        save_location = tmp_path / "latest.pkl"
        upload_state = _make_upload_state(save_location)
        persist_state_for_resume(upload_state)
        out = capsys.readouterr().out
        assert save_location.exists()
        assert str(save_location) in out
        assert "resume-xmlupload" in out

    def test_mentions_failed_uploads(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        upload_state = _make_upload_state(tmp_path / "latest.pkl")
        upload_state.failed_uploads = ["bar_id"]
        persist_state_for_resume(upload_state)
        out = capsys.readouterr().out
        assert "bar_id" in out
