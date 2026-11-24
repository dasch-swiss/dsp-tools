from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import pytest

from dsp_tools.commands.ingest_xmlupload.delete_data_import import _delete
from dsp_tools.commands.ingest_xmlupload.exceptions import SystemAdminRequiredError
from dsp_vre.clients.data_import_client import DataImportId
from dsp_vre.clients.data_import_client import DataImportStatus
from dsp_vre.clients.data_import_client import DataImportStatusValue
from dsp_vre.clients.exceptions import BadCredentialsError
from dsp_vre.clients.exceptions import DataImportInProgressError
from dsp_vre.clients.exceptions import DataImportNotFoundError

IMPORT_ID = "imp-1"


def _status(value: DataImportStatusValue, error: str | None = None) -> DataImportStatus:
    return DataImportStatus(DataImportId(IMPORT_ID), "http://rdfh.ch/projects/x", value, error)


@dataclass(frozen=True)
class FakeClient:
    status: DataImportStatus | Exception = field(default_factory=Exception)
    delete_error: Exception | None = None
    deleted: list[DataImportId] = field(default_factory=list)

    def get_status(self, import_id: DataImportId) -> DataImportStatus:  # noqa: ARG002
        if isinstance(self.status, Exception):
            raise self.status
        return self.status

    def delete_import(self, import_id: DataImportId) -> None:
        self.deleted.append(import_id)
        if self.delete_error:
            raise self.delete_error


def _run(client: FakeClient, shortcode: str, import_id: str, error_folder: Path) -> bool:
    return _delete(client, shortcode, import_id, error_folder)  # type: ignore[arg-type]


def test_in_progress(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(_status(DataImportStatusValue.IN_PROGRESS))
    assert _run(client, "0001", IMPORT_ID, tmp_path) is False
    assert client.deleted == []
    assert "cannot be deleted" in capsys.readouterr().out


def test_failed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(_status(DataImportStatusValue.FAILED, "bad data"))
    assert _run(client, "0001", IMPORT_ID, tmp_path) is True
    error_file = tmp_path / "0001_imp-1_error.txt"
    assert error_file.read_text(encoding="utf-8") == "bad data"
    assert client.deleted == [DataImportId(IMPORT_ID)]
    out = capsys.readouterr().out
    assert str(error_file) in out
    assert "was deleted" in out


def test_completed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(_status(DataImportStatusValue.COMPLETED))
    assert _run(client, "0001", IMPORT_ID, tmp_path) is True
    assert client.deleted == [DataImportId(IMPORT_ID)]
    assert not list(tmp_path.iterdir())
    assert "was deleted" in capsys.readouterr().out


def test_not_found_on_get(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(DataImportNotFoundError(IMPORT_ID, "m"))
    assert _run(client, "0001", IMPORT_ID, tmp_path) is True
    assert client.deleted == []
    assert "does not exist" in capsys.readouterr().out


def test_not_found_on_delete(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(_status(DataImportStatusValue.COMPLETED), delete_error=DataImportNotFoundError(IMPORT_ID, "m"))
    assert _run(client, "0001", IMPORT_ID, tmp_path) is True
    assert "does not exist" in capsys.readouterr().out


def test_in_progress_on_delete(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(
        _status(DataImportStatusValue.COMPLETED), delete_error=DataImportInProgressError(IMPORT_ID, "m")
    )
    assert _run(client, "0001", IMPORT_ID, tmp_path) is False
    assert "cannot be deleted" in capsys.readouterr().out


@pytest.mark.parametrize("on_delete", [False, True])
def test_bad_credentials(tmp_path: Path, on_delete: bool) -> None:
    error = BadCredentialsError("x")
    if on_delete:
        client = FakeClient(_status(DataImportStatusValue.COMPLETED), delete_error=error)
    else:
        client = FakeClient(error)
    with pytest.raises(SystemAdminRequiredError, match="delete-data-import"):
        _run(client, "0001", IMPORT_ID, tmp_path)
