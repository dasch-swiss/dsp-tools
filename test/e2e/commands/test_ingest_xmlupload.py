from pathlib import Path

import pytest

from dsp_tools.commands.ingest_xmlupload.upload_xml import ingest_xmlupload
from dsp_tools.models.exceptions import InputError


@pytest.fixture()
def base_path() -> Path:
    """Get the root directory of the repository."""
    return Path(__file__).parents[3]


def test_ingest_xmlupload(base_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path(base_path, "testdata/dsp-ingest-data"))
    expected_msg = (
        "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
        "    The data XML file does not reference the following multimedia files "
        "which were previously uploaded through dsp-ingest:\n"
        "    - extra.jpg\n"
        "    The data XML file contains references to the following multimedia files "
        "which were not previously uploaded through dsp-ingest:\n"
        "    - Resource ID: 'GoodGirlImage' | Filepath: 'images/GoodGirl.jpg'"
    )
    with pytest.raises(InputError, match=expected_msg):
        ingest_xmlupload(
            xml_file=Path("dsp-ingest.xml"),
            user="root@example.com",
            password="test",
            dsp_url="http://0.0.0.0:3333",
            sipi_url="http://0.0.0.0:1024",
        )


def test_ingest_xmlupload_no_mapping() -> None:
    with pytest.raises(InputError):
        ingest_xmlupload(
            xml_file=Path("testdata/dsp-ingest-data/dsp_ingest_no_mapping.xml"),
            user="root@example.com",
            password="test",
            dsp_url="http://0.0.0.0:3333",
            sipi_url="http://0.0.0.0:1024",
        )


if __name__ == "__main__":
    pytest.main([__file__])
