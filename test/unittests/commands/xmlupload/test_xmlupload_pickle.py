from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.xmlupload_pickle import XmlUploadPickle
from dsp_tools.commands.xmlupload.models.xmlupload_pickle import load_pickle
from dsp_tools.commands.xmlupload.models.xmlupload_pickle import save_pickle


def _make_resource(res_id: str) -> ProcessedResource:
    return ProcessedResource(
        res_id=res_id,
        type_iri="http://0.0.0.0/onto#Thing",
        label="label",
        permissions=None,
        values=[],
    )


def test_pickle_round_trip(tmp_path: Path) -> None:
    data = XmlUploadPickle(
        sorted_resources=[_make_resource("r1"), _make_resource("r2")],
        stash=None,
        shortcode="0001",
    )
    pkl_file = tmp_path / "upload.pkl"
    save_pickle(data, pkl_file)
    loaded = load_pickle(pkl_file)
    assert loaded.shortcode == "0001"
    assert loaded.stash is None
    assert len(loaded.sorted_resources) == 2
    assert loaded.sorted_resources[0].res_id == "r1"
    assert loaded.sorted_resources[1].res_id == "r2"


def test_load_pickle_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_pickle(tmp_path / "nonexistent.pkl")
