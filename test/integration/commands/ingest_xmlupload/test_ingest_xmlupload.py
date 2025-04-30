import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
import regex

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.error.exceptions import InputError


@pytest.fixture(autouse=True)
def _retrieve_mapping_file() -> Iterator[None]:
    """Put the mapping file into the cwd."""
    mapping_file = Path("testdata/dsp-ingest-data/mapping-00A2.csv")
    shutil.copy(mapping_file, ".")
    yield
    Path(mapping_file.name).unlink()


@pytest.fixture
def creds() -> ServerCredentials:
    return ServerCredentials(
        user="root@example.com",
        password="test",
        server="http://0.0.0.0:3333",
        dsp_ingest_url="http://0.0.0.0:3340",
    )


def test_ingest_xmlupload(creds: ServerCredentials) -> None:
    expected_msg = regex.escape(
        "The upload cannot continue as there are problems with the multimedia files referenced in the XML.\n"
        "    The data XML file does not reference the following multimedia files "
        "which were previously uploaded through dsp-ingest:\n"
        "    - extra.jpg\n"
        "    The data XML file contains references to the following multimedia files "
        "which were not previously uploaded through dsp-ingest:\n"
        "    - Resource ID: 'GoodGirlImage' | Filepath: 'images/GoodGirl.jpg'"
    )
    with pytest.raises(InputError, match=expected_msg):
        ingest_xmlupload(xml_file=Path("testdata/dsp-ingest-data/dsp-ingest.xml"), creds=creds)


def test_ingest_xmlupload_no_mapping(creds: ServerCredentials) -> None:
    expected_msg = regex.escape("No mapping CSV file was found at mapping-00A5.csv.")
    with pytest.raises(InputError, match=expected_msg):
        ingest_xmlupload(xml_file=Path("testdata/dsp-ingest-data/dsp_ingest_no_mapping.xml"), creds=creds)


if __name__ == "__main__":
    pytest.main([__file__])
