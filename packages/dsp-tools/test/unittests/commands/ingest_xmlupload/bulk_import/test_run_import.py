import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout

from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import PayloadFiles
from dsp_tools.commands.ingest_xmlupload.bulk_import.run_import import run_import
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportConnectionLostError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportExistsError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportNotEnabledError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportPreconditionError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportRunningError
from dsp_tools.commands.ingest_xmlupload.exceptions import OnBehalfOfUserMissingError
from dsp_tools.commands.ingest_xmlupload.exceptions import OnBehalfOfUserRejectedError
from dsp_tools.commands.ingest_xmlupload.exceptions import PayloadSendConnectionLostError
from dsp_tools.commands.ingest_xmlupload.exceptions import PayloadTooLargeError
from dsp_tools.commands.ingest_xmlupload.exceptions import SystemAdminRequiredError
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import UserError
from dsp_vre.clients.data_import_client import DataImportId
from dsp_vre.clients.data_import_client import DataImportStatus
from dsp_vre.clients.data_import_client import DataImportStatusValue
from dsp_vre.clients.exceptions import BadCredentialsError
from dsp_vre.clients.exceptions import DataImportExistsError
from dsp_vre.clients.exceptions import DataImportNotEnabledError
from dsp_vre.clients.exceptions import DataImportPayloadTooLargeError
from dsp_vre.clients.exceptions import DataImportPreconditionError
from dsp_vre.clients.exceptions import DataImportRunningError
from dsp_vre.clients.exceptions import OnBehalfOfUserIneligibleError
from dsp_vre.clients.exceptions import OnBehalfOfUserNotFoundError

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning:yaspin")

IMPORT_ID = DataImportId("imp-1")
MIB = 1024 * 1024
WRITE_MAPPING = "dsp_tools.commands.ingest_xmlupload.bulk_import.run_import.write_id2iri_mapping"


def _status(value: DataImportStatusValue, error: str | None = None) -> DataImportStatus:
    return DataImportStatus(IMPORT_ID, "http://rdfh.ch/projects/x", value, error)


IN_PROGRESS = _status(DataImportStatusValue.IN_PROGRESS)
COMPLETED = _status(DataImportStatusValue.COMPLETED)
FAILED = _status(DataImportStatusValue.FAILED, "bad data")


@dataclass(frozen=True)
class FakeClient:
    server: str = "http://0.0.0.0:3333"
    project_iri: str = "http://rdfh.ch/projects/x"
    auth: None = None
    post_error: BaseException | None = None
    statuses: list[DataImportStatus | BaseException] = field(default_factory=list)
    delete_error: Exception | None = None
    deleted: list[DataImportId] = field(default_factory=list)

    def post_import(self, payload_path: Path, on_behalf_of_user: str) -> DataImportId:  # noqa: ARG002
        if self.post_error:
            raise self.post_error
        return IMPORT_ID

    def get_status(self, import_id: DataImportId) -> DataImportStatus:  # noqa: ARG002
        item = self.statuses.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    def delete_import(self, import_id: DataImportId) -> None:
        self.deleted.append(import_id)
        if self.delete_error:
            raise self.delete_error


@pytest.fixture
def files(tmp_path: Path) -> PayloadFiles:
    result = PayloadFiles(tmp_path / "p.jsonld", tmp_path / "p_id2iri.json", tmp_path / "p_error.txt")
    result.payload.write_bytes(b"x" * 2 * MIB)
    result.id2iri.write_text("{}", encoding="utf-8")
    return result


def _run(client: FakeClient, files: PayloadFiles, tmp_path: Path) -> bool:
    diagnostics = DiagnosticsConfig("localhost", tmp_path / "save")
    return run_import(client, files, "user@x.org", "0001", {"a": "b"}, diagnostics, sleep_time=0)  # type: ignore[arg-type]


def test_completed(files: PayloadFiles, tmp_path: Path) -> None:
    client = FakeClient(statuses=[COMPLETED])
    with patch(WRITE_MAPPING) as write_mapping:
        assert _run(client, files, tmp_path) is True
    write_mapping.assert_called_once()
    assert write_mapping.call_args.args[:2] == ({"a": "b"}, "0001")
    assert client.deleted == [IMPORT_ID]
    assert not files.payload.exists()
    assert not files.id2iri.exists()


def test_in_progress_then_completed(files: PayloadFiles, tmp_path: Path) -> None:
    client = FakeClient(statuses=[IN_PROGRESS, IN_PROGRESS, COMPLETED])
    with patch(WRITE_MAPPING):
        assert _run(client, files, tmp_path) is True
    assert client.deleted == [IMPORT_ID]


def test_completed_delete_fails(files: PayloadFiles, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(statuses=[COMPLETED], delete_error=DataImportRunningError("busy"))
    with patch(WRITE_MAPPING):
        assert _run(client, files, tmp_path) is True
    out = capsys.readouterr().out
    assert "imp-1" in out
    assert "uvx dsp-tools delete-data-import 0001 imp-1" in out


def test_failed(files: PayloadFiles, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(statuses=[FAILED])
    assert _run(client, files, tmp_path) is False
    assert files.error.read_text(encoding="utf-8") == "bad data"
    assert str(files.error) in capsys.readouterr().out
    assert client.deleted == [IMPORT_ID]
    assert files.payload.exists()
    assert files.id2iri.exists()


def test_failed_delete_fails(files: PayloadFiles, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    client = FakeClient(statuses=[FAILED], delete_error=DataImportRunningError("busy"))
    assert _run(client, files, tmp_path) is False
    out = capsys.readouterr().out
    assert "imp-1" in out
    assert "uvx dsp-tools delete-data-import 0001 imp-1" in out


def test_failed_error_file_not_writable(
    files: PayloadFiles, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken = PayloadFiles(files.payload, files.id2iri, tmp_path / "missing-folder" / "e.txt")
    client = FakeClient(statuses=[FAILED])
    assert _run(client, broken, tmp_path) is False
    assert client.deleted == [IMPORT_ID]
    assert "bad data" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("post_error", "expected", "text"),
    [
        (BadCredentialsError("x"), SystemAdminRequiredError, "not a system admin"),
        (OnBehalfOfUserNotFoundError("u", "m"), OnBehalfOfUserMissingError, "does not exist"),
        (
            OnBehalfOfUserIneligibleError("u", "is_system_admin", "m"),
            OnBehalfOfUserRejectedError,
            "not a system admin",
        ),
        (OnBehalfOfUserIneligibleError("u", "not_project_member", "m"), OnBehalfOfUserRejectedError, "not a member"),
        (OnBehalfOfUserIneligibleError("u", "inactive", "m"), OnBehalfOfUserRejectedError, "not active"),
        (OnBehalfOfUserIneligibleError("u", "cannot_create", "m"), OnBehalfOfUserRejectedError, "no create rights"),
        (
            OnBehalfOfUserIneligibleError("u", "malformed_identifier", "m"),
            OnBehalfOfUserRejectedError,
            "neither an email nor a username",
        ),
        (OnBehalfOfUserIneligibleError("u", "weird_code", "m"), OnBehalfOfUserRejectedError, "weird_code"),
        (
            DataImportExistsError("imp-9", "iri", "m"),
            BulkImportExistsError,
            "uvx dsp-tools delete-data-import 0001 imp-9",
        ),
        (DataImportRunningError("m"), BulkImportRunningError, r"Another import \(bulk or migration\) is running"),
        (
            DataImportPreconditionError("data_graph_exists", "graph there"),
            BulkImportPreconditionError,
            "no data except list nodes",
        ),
        (
            DataImportPreconditionError("project_ontologies_missing", "no onto"),
            BulkImportPreconditionError,
            "no onto",
        ),
        (DataImportNotEnabledError("m"), BulkImportNotEnabledError, "not enabled"),
        (DataImportPayloadTooLargeError(300 * MIB, 250 * MIB, "m"), PayloadTooLargeError, "300.0 MiB"),
        (DataImportPayloadTooLargeError(None, None, "m"), PayloadTooLargeError, "2.0 MiB"),
    ],
)
def test_post_rejected(
    post_error: Exception, expected: type[UserError], text: str, files: PayloadFiles, tmp_path: Path
) -> None:
    client = FakeClient(post_error=post_error)
    with pytest.raises(expected, match=text):
        _run(client, files, tmp_path)
    assert not files.payload.exists()
    assert not files.id2iri.exists()


def test_post_too_large_unknown_uses_default_limit(files: PayloadFiles, tmp_path: Path) -> None:
    with pytest.raises(PayloadTooLargeError, match=r"2\.0 MiB\. The default server limit is 250 MiB"):
        _run(FakeClient(post_error=DataImportPayloadTooLargeError(None, None, "m")), files, tmp_path)


def test_precondition_names_folder(files: PayloadFiles, tmp_path: Path) -> None:
    client = FakeClient(post_error=DataImportPreconditionError("data_graph_exists", "m"))
    with pytest.raises(BulkImportPreconditionError, match=str(files.payload.parent)):
        _run(client, files, tmp_path)


@pytest.mark.parametrize("error", [RequestsConnectionError("x"), Timeout("x")])
def test_post_connection_error_keeps_files(error: Exception, files: PayloadFiles, tmp_path: Path) -> None:
    with pytest.raises(PayloadSendConnectionLostError, match=r"2\.0 MiB\. The default server limit is 250 MiB"):
        _run(FakeClient(post_error=error), files, tmp_path)
    assert files.payload.exists()
    assert files.id2iri.exists()


def test_post_keyboard_interrupt(files: PayloadFiles, tmp_path: Path) -> None:
    with pytest.warns(DspToolsUserWarning, match="may hold a task"), pytest.raises(KeyboardInterrupt):
        _run(FakeClient(post_error=KeyboardInterrupt()), files, tmp_path)
    assert files.payload.exists()
    assert files.id2iri.exists()


def test_poll_keyboard_interrupt(files: PayloadFiles, tmp_path: Path) -> None:
    client = FakeClient(statuses=[KeyboardInterrupt()])
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        with pytest.raises(KeyboardInterrupt):
            _run(client, files, tmp_path)
    message = next(str(w.message) for w in record if isinstance(w.message, DspToolsUserWarning))
    assert str(files.payload) in message
    assert str(files.id2iri) in message
    assert "uvx dsp-tools delete-data-import 0001 imp-1" in message


@pytest.mark.parametrize("error", [RequestsConnectionError("x"), Timeout("x")])
def test_poll_connection_error(error: Exception, files: PayloadFiles, tmp_path: Path) -> None:
    client = FakeClient(statuses=[IN_PROGRESS, error])
    with pytest.raises(BulkImportConnectionLostError) as exc_info:
        _run(client, files, tmp_path)
    message = str(exc_info.value)
    assert "imp-1" in message
    assert str(files.payload) in message
    assert str(files.id2iri) in message
    assert client.deleted == []
