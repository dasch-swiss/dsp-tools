# mypy: disable-error-code="method-assign,no-untyped-def"

from copy import deepcopy

import pytest

from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _tidy_up_resource_creation_idempotent


@pytest.fixture
def processed_resources() -> list[ProcessedResource]:
    one = ProcessedResource("foo_1_id", "onto:foo_1_type", "lbl", None, [ProcessedSimpleText("val", "prp", None, None)])
    two = ProcessedResource("foo_2_id", "onto:foo_2_type", "lbl", None, [ProcessedSimpleText("val", "prp", None, None)])
    return [one, two]


def test_idempotency_on_success(processed_resources) -> None:
    upload_state = UploadState(deepcopy(processed_resources), None, UploadConfig())
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, "foo_1_iri", processed_resources[0])
        assert upload_state.pending_resources == processed_resources[1:]
        assert upload_state.failed_uploads == []
        assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri"}
        assert not upload_state.pending_stash


def test_idempotency_on_failure(processed_resources) -> None:
    upload_state = UploadState(deepcopy(processed_resources), None, UploadConfig())
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, None, processed_resources[0])
        assert upload_state.pending_resources == processed_resources[1:]
        assert upload_state.failed_uploads == ["foo_1_id"]
        assert upload_state.iri_resolver.lookup == {}
        assert not upload_state.pending_stash
