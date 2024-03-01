import shutil
from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.commands.ingest_xmlupload.upload_xml import ingest_xmlupload
from dsp_tools.models.exceptions import InputError


@pytest.fixture(autouse=True)
def _retrieve_mapping_file() -> Iterator[None]:
    """Put the mapping file into the cwd."""
    mapping_file = Path("testdata/dsp-ingest-data/mapping-00A2.csv")
    shutil.copy(mapping_file, ".")
    yield
    Path(mapping_file.name).unlink()


def test_ingest_xmlupload() -> None:
    expected_msg = (
        r"The upload cannot continue as there are problems with the multimedia files referenced in the XML\.\n"
        r"    The data XML file does not reference the following multimedia files "
        r"which were previously uploaded through dsp-ingest:\n"
        r"    - extra\.jpg\n"
        r"    The data XML file contains references to the following multimedia files "
        r"which were not previously uploaded through dsp-ingest:\n"
        r"    - Resource ID: 'GoodGirlImage' \| Filepath: 'images/GoodGirl\.jpg'"
    )
    with pytest.raises(InputError, match=expected_msg):
        ingest_xmlupload(
            xml_file=Path("testdata/dsp-ingest-data/dsp-ingest.xml"),
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
