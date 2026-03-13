from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.execute_upload import _execute_one_resource_data_upload
from dsp_tools.commands.xmlupload.execute_upload import _execute_one_resource_upload
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

MODULE = "dsp_tools.commands.xmlupload.execute_upload"


@pytest.fixture
def resource() -> ProcessedResource:
    return ProcessedResource(
        res_id="res_id",
        type_iri="onto:Type",
        label="label",
        permissions=None,
        values=[],
        file_value=None,
    )


@pytest.fixture
def resource_with_file() -> ProcessedResource:
    metadata = ProcessedFileMetadata(
        license_iri="http://rdfh.ch/licenses/cc-by-4.0",
        copyright_holder="Test Author",
        authorships=["Test Author"],
    )
    file_value = ProcessedFileValue(
        value="test.jpg",
        file_type=KnoraValueType.STILL_IMAGE_FILE,
        metadata=metadata,
        res_id="res_id",
        res_label="label",
    )
    return ProcessedResource(
        res_id="res_id",
        type_iri="onto:Type",
        label="label",
        permissions=None,
        values=[],
        file_value=file_value,
    )


@pytest.fixture
def upload_state(resource: ProcessedResource) -> UploadState:
    return UploadState(
        pending_resources=[resource],
        pending_stash=None,
        config=UploadConfig(),
    )


@pytest.fixture
def resource_client() -> MagicMock:
    return MagicMock(spec=ResourceClient)


@pytest.fixture
def ingest_client() -> MagicMock:
    return MagicMock(spec=AssetClient)


@pytest.fixture
def iri_lookups() -> MagicMock:
    return MagicMock(spec=IRILookups)


@pytest.fixture
def resource_upload_patches():
    with (
        patch(f"{MODULE}._execute_one_resource_data_upload", return_value="http://created_iri") as mock_data_upload,
        patch(f"{MODULE}.tidy_up_resource_creation_idempotent"),
        patch(f"{MODULE}.interrupt_if_indicated"),
        patch(f"{MODULE}.handle_permanent_connection_error", side_effect=XmlUploadInterruptedError("conn")),
        patch(f"{MODULE}.handle_keyboard_interrupt", side_effect=XmlUploadInterruptedError("kbd")),
        patch(
            f"{MODULE}.handle_permanent_timeout_or_keyboard_interrupt",
            side_effect=XmlUploadInterruptedError("timeout"),
        ),
        patch(f"{MODULE}.inform_about_resource_creation_failure"),
    ):
        yield mock_data_upload


class TestExecuteOneUpload:
    def test_upload_no_file_value(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        mock_data_upload = resource_upload_patches
        _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

        ingest_client.get_bitstream_info.assert_not_called()
        mock_data_upload.assert_called_once()
        _, kwargs = mock_data_upload.call_args
        assert kwargs.get("media_info") is None or mock_data_upload.call_args[0][1] is None

    def test_upload_with_file_value(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        mock_data_upload = resource_upload_patches
        bitstream = BitstreamInfo("internal.jpg")
        ingest_client.get_bitstream_info.return_value = bitstream
        upload_state.pending_resources = [resource_with_file]

        _execute_one_resource_upload(resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0)

        mock_data_upload.assert_called_once()
        call_args = mock_data_upload.call_args[0]
        assert call_args[1] == bitstream

    def test_upload_ingest_returns_none(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        mock_data_upload = resource_upload_patches
        ingest_client.get_bitstream_info.return_value = None
        upload_state.pending_resources = [resource_with_file]

        _execute_one_resource_upload(resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0)

        assert resource_with_file.res_id in upload_state.failed_uploads
        mock_data_upload.assert_not_called()

    def test_upload_ingest_permanent_connection_error(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        ingest_client.get_bitstream_info.side_effect = PermanentConnectionError("conn err")
        upload_state.pending_resources = [resource_with_file]

        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(
                resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0
            )

    def test_upload_ingest_keyboard_interrupt(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        ingest_client.get_bitstream_info.side_effect = KeyboardInterrupt()
        upload_state.pending_resources = [resource_with_file]

        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(
                resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0
            )

    def test_upload_data_permanent_timeout(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        mock_data_upload = resource_upload_patches
        mock_data_upload.side_effect = PermanentTimeOutError("timeout")

        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

    def test_upload_data_permanent_connection_error(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
        resource_upload_patches: MagicMock,
    ) -> None:
        mock_data_upload = resource_upload_patches
        mock_data_upload.side_effect = PermanentConnectionError("conn err")

        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

    def test_upload_data_generic_exception(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
    ) -> None:
        with (
            patch(f"{MODULE}._execute_one_resource_data_upload", side_effect=Exception("oops")),
            patch(f"{MODULE}.tidy_up_resource_creation_idempotent") as mock_tidy,
            patch(f"{MODULE}.interrupt_if_indicated"),
            patch(f"{MODULE}.handle_permanent_connection_error", side_effect=XmlUploadInterruptedError("conn")),
            patch(f"{MODULE}.handle_keyboard_interrupt", side_effect=XmlUploadInterruptedError("kbd")),
            patch(
                f"{MODULE}.handle_permanent_timeout_or_keyboard_interrupt",
                side_effect=XmlUploadInterruptedError("timeout"),
            ),
            patch(f"{MODULE}.inform_about_resource_creation_failure") as mock_inform,
        ):
            _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

        mock_inform.assert_called_once()
        mock_tidy.assert_called_once()
        call_kwargs = mock_tidy.call_args
        assert call_kwargs[0][1] is None or call_kwargs.kwargs.get("iri") is None

    def test_upload_keyboard_interrupt_in_tidy_up(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: MagicMock,
    ) -> None:
        with (
            patch(f"{MODULE}._execute_one_resource_data_upload", return_value="http://created_iri"),
            patch(
                f"{MODULE}.tidy_up_resource_creation_idempotent",
                side_effect=[KeyboardInterrupt(), None],
            ) as mock_tidy,
            patch(f"{MODULE}.interrupt_if_indicated"),
            patch(f"{MODULE}.handle_permanent_connection_error", side_effect=XmlUploadInterruptedError("conn")),
            patch(f"{MODULE}.handle_keyboard_interrupt", side_effect=XmlUploadInterruptedError("kbd")),
            patch(
                f"{MODULE}.handle_permanent_timeout_or_keyboard_interrupt",
                side_effect=XmlUploadInterruptedError("timeout"),
            ),
            patch(f"{MODULE}.inform_about_resource_creation_failure"),
        ):
            with pytest.raises(XmlUploadInterruptedError):
                _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

        assert mock_tidy.call_count == 2


@pytest.fixture
def data_upload_patches():
    with (
        patch(f"{MODULE}.create_resource_with_values", return_value=MagicMock()),
        patch(f"{MODULE}.serialise_jsonld_for_resource", return_value={}),
        patch(f"{MODULE}.log_request_failure_and_sleep"),
        patch(f"{MODULE}.is_server_error", return_value=False),
    ):
        yield


class TestResourceDataUpload:
    def test_data_upload_success_first_try(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: MagicMock,
        data_upload_patches: None,
    ) -> None:
        resource_client.post_resource.return_value = "http://created_iri"

        result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)

        assert result == "http://created_iri"
        assert resource_client.post_resource.call_count == 1

    def test_data_upload_non_retryable_failure(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: MagicMock,
        data_upload_patches: None,
    ) -> None:
        resource_client.post_resource.return_value = ResponseCodeAndText(400, "bad")

        with patch(f"{MODULE}.is_server_error", return_value=False):
            result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)

        assert result is None
        assert resource_client.post_resource.call_count == 1

    def test_data_upload_retry_then_success(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: MagicMock,
    ) -> None:
        with (
            patch(f"{MODULE}.create_resource_with_values", return_value=MagicMock()),
            patch(f"{MODULE}.serialise_jsonld_for_resource", return_value={}),
            patch(f"{MODULE}.is_server_error", return_value=False),
            patch(f"{MODULE}.log_request_failure_and_sleep") as mock_sleep,
        ):
            resource_client.post_resource.side_effect = [DspToolsRequestException("err"), "http://created_iri"]

            result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)

        assert result == "http://created_iri"
        assert resource_client.post_resource.call_count == 2
        assert mock_sleep.call_count == 1

    def test_data_upload_retry_exhaustion(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: MagicMock,
    ) -> None:
        with (
            patch(f"{MODULE}.create_resource_with_values", return_value=MagicMock()),
            patch(f"{MODULE}.serialise_jsonld_for_resource", return_value={}),
            patch(f"{MODULE}.is_server_error", return_value=False),
            patch(f"{MODULE}.log_request_failure_and_sleep"),
        ):
            resource_client.post_resource.side_effect = DspToolsRequestException("err")

            with pytest.raises(PermanentConnectionError):
                _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)

        assert resource_client.post_resource.call_count == 24
