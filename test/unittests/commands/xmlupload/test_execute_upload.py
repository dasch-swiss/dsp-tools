from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from rdflib import URIRef

from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.execute_upload import _execute_one_resource_data_upload
from dsp_tools.commands.xmlupload.execute_upload import _execute_one_resource_upload
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

RES_ID = "res_id"
RES_IRI = "http://iri/res_id"


@pytest.fixture
def resource() -> ProcessedResource:
    return ProcessedResource(
        res_id=RES_ID,
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
        res_id=RES_ID,
        res_label="label",
    )
    return ProcessedResource(
        res_id=RES_ID,
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
def iri_lookups() -> IRILookups:
    return IRILookups(
        project_iri=URIRef("http://rdfh.ch/projects/test"),
        id_to_iri=IriResolver(),
    )


@pytest.fixture(autouse=True)
def patch_sleep():
    with patch("dsp_tools.utils.request_utils.time.sleep"):
        yield


class TestExecuteOneUpload:
    def test_upload_no_file_value(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.return_value = RES_IRI
        _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)
        ingest_client.get_bitstream_info.assert_not_called()
        assert upload_state.iri_resolver.lookup == {RES_ID: RES_IRI}

    def test_upload_with_file_value(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        ingest_client.get_bitstream_info.return_value = BitstreamInfo("internal.jpg")
        resource_client.post_resource.return_value = RES_IRI
        upload_state.pending_resources = [resource_with_file]
        _execute_one_resource_upload(resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0)
        assert upload_state.iri_resolver.lookup == {RES_ID: RES_IRI}

    def test_upload_ingest_returns_none(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        ingest_client.get_bitstream_info.return_value = None
        upload_state.pending_resources = [resource_with_file]
        _execute_one_resource_upload(resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0)
        assert RES_ID in upload_state.failed_uploads

    def test_upload_ingest_permanent_connection_error(
        self,
        resource_with_file: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
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
        iri_lookups: IRILookups,
    ) -> None:
        ingest_client.get_bitstream_info.side_effect = KeyboardInterrupt()
        upload_state.pending_resources = [resource_with_file]
        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(
                resource_with_file, upload_state, resource_client, ingest_client, iri_lookups, 0
            )

    def test_upload_data_permanent_connection_error(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.side_effect = PermanentConnectionError("conn err")
        with pytest.raises(XmlUploadInterruptedError):
            _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)

    def test_upload_keyboard_interrupt_in_tidy_up(
        self,
        resource: ProcessedResource,
        upload_state: UploadState,
        resource_client: MagicMock,
        ingest_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.return_value = RES_IRI
        with patch(
            "dsp_tools.commands.xmlupload.execute_upload.tidy_up_resource_creation_idempotent",
            side_effect=[KeyboardInterrupt(), None],
        ) as mock_tidy:
            with pytest.raises(XmlUploadInterruptedError):
                _execute_one_resource_upload(resource, upload_state, resource_client, ingest_client, iri_lookups, 0)
        assert mock_tidy.call_count == 2


class TestResourceDataUpload:
    def test_data_upload_success_first_try(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.return_value = RES_IRI
        result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)
        assert result == RES_IRI
        assert resource_client.post_resource.call_count == 1

    def test_data_upload_non_retryable_failure(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.return_value = ResponseCodeAndText(400, "bad")
        result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)
        assert result is None
        assert resource_client.post_resource.call_count == 1

    def test_data_upload_retry_then_success(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.side_effect = [DspToolsRequestException("err"), RES_IRI]
        result = _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)
        assert result == RES_IRI
        assert resource_client.post_resource.call_count == 2

    def test_data_upload_retry_exhaustion(
        self,
        resource: ProcessedResource,
        resource_client: MagicMock,
        iri_lookups: IRILookups,
    ) -> None:
        resource_client.post_resource.side_effect = DspToolsRequestException("err")
        with pytest.raises(PermanentConnectionError):
            _execute_one_resource_data_upload(resource, None, resource_client, iri_lookups)
        assert resource_client.post_resource.call_count == 24
