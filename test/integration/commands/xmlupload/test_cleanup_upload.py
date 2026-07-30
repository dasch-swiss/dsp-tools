from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from dsp_tools.commands.xmlupload.execute_upload import cleanup_upload
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.upload_config import UploadConfig

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
LINK_PROP = f"{ONTO}hasCustomLink"


@pytest.fixture(autouse=True)
def _no_id2iri_files() -> Iterator[None]:
    # cleanup_upload always writes an id2iri mapping to the cwd and home dir; suppress that side effect.
    with patch("dsp_tools.commands.xmlupload.execute_upload.write_id2iri_mapping"):
        yield


@pytest.fixture
def save_location(tmp_path: Path) -> Path:
    return tmp_path / "latest.pkl"


def _make_upload_state(save_location: Path, failed_uploads: list[str], stash: Stash | None) -> UploadState:
    config = UploadConfig(diagnostics=DiagnosticsConfig(save_location=save_location))
    return UploadState(
        pending_resources=[],
        pending_stash=stash,
        config=config,
        failed_uploads=failed_uploads,
        iri_resolver=IriResolver({"foo": "bar"}),
    )


def _non_empty_stash() -> Stash:
    stash_item = LinkValueStashItem(
        "foo_id", f"{ONTO}foo_type", ProcessedLink("bar_id", LINK_PROP, None, None, None, str(uuid4()))
    )
    return Stash(standoff_stash=None, link_value_stash=LinkValueStash({"foo_id": [stash_item]}))


def test_all_successful_does_not_save_pickle(save_location: Path, capsys: pytest.CaptureFixture[str]) -> None:
    upload_state = _make_upload_state(save_location, failed_uploads=[], stash=None)
    success = cleanup_upload(upload_state)
    out = capsys.readouterr().out
    assert success is True
    assert not save_location.exists()
    assert "All resources have successfully been uploaded." in out
    assert "Saved the current upload state" not in out


def test_failures_only_does_not_save_pickle(save_location: Path, capsys: pytest.CaptureFixture[str]) -> None:
    upload_state = _make_upload_state(save_location, failed_uploads=["res_a", "res_b"], stash=None)
    success = cleanup_upload(upload_state)
    out = capsys.readouterr().out
    assert success is False
    assert not save_location.exists()
    assert "Could not upload the following resources" in out
    assert "Saved the current upload state" not in out


def test_stash_present_saves_pickle(
    save_location: Path, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
) -> None:
    upload_state = _make_upload_state(save_location, failed_uploads=[], stash=_non_empty_stash())
    success = cleanup_upload(upload_state)
    out = capsys.readouterr().out
    assert success is False
    assert save_location.exists()
    # console: count only, no per-item details
    assert "Could not reapply 1 stashed values" in out
    assert "hasCustomLink" not in out
    # log: resource / property combinations
    assert "resource / property" in caplog.text
    assert f"foo_id / {LINK_PROP}Value" in caplog.text
    assert "Saved the current upload state" in out


def test_stash_and_failures_saves_pickle(
    save_location: Path, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
) -> None:
    upload_state = _make_upload_state(save_location, failed_uploads=["res_a"], stash=_non_empty_stash())
    success = cleanup_upload(upload_state)
    out = capsys.readouterr().out
    assert success is False
    assert save_location.exists()
    assert "Could not upload the following resources" in out
    assert "Could not reapply 1 stashed values" in out
    assert f"foo_id / {LINK_PROP}Value" in caplog.text
    assert "Saved the current upload state" in out
