from copy import deepcopy

import pytest

from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _tidy_up_resource_creation_idempotent


@pytest.fixture
def intermediary_resources() -> list[IntermediaryResource]:
    one = IntermediaryResource(
        "foo_1_id", "onto:foo_1_type", "lbl", None, [IntermediarySimpleText("val", "prp", None, None)]
    )
    two = IntermediaryResource(
        "foo_2_id", "onto:foo_2_type", "lbl", None, [IntermediarySimpleText("val", "prp", None, None)]
    )
    return [one, two]


def test_idempotency_on_success(intermediary_resources: list[IntermediaryResource]) -> None:
    upload_state = UploadState(deepcopy(intermediary_resources), None, UploadConfig(), JSONLDContext({}))
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, "foo_1_iri", intermediary_resources[0])
        assert upload_state.pending_resources == intermediary_resources[1:]
        assert upload_state.failed_uploads == []
        assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri"}
        assert not upload_state.pending_stash


def test_idempotency_on_failure(intermediary_resources: list[IntermediaryResource]) -> None:
    upload_state = UploadState(deepcopy(intermediary_resources), None, UploadConfig(), JSONLDContext({}))
    for _ in range(3):
        _tidy_up_resource_creation_idempotent(upload_state, None, intermediary_resources[0])
        assert upload_state.pending_resources == intermediary_resources[1:]
        assert upload_state.failed_uploads == ["foo_1_id"]
        assert upload_state.iri_resolver.lookup == {}
        assert not upload_state.pending_stash
