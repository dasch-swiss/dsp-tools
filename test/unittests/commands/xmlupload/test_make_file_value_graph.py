import pytest
import regex
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.make_file_value_graph import _add_metadata
from dsp_tools.commands.xmlupload.make_file_value_graph import _get_file_type_info
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import FileValueMetadata
from dsp_tools.models.exceptions import BaseError

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


class TestFileTypeInfo:
    @pytest.mark.parametrize(
        "file_name", ["test.zip", "test.tar", "test.gz", "test.z", "test.tgz", "test.gzip", "test.7z"]
    )
    def test_archive(self, file_name: str) -> None:
        result = _get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.ArchiveFileValue

    @pytest.mark.parametrize("file_name", ["test.mp3", "test.wav"])
    def test_audio(self, file_name: str) -> None:
        result = _get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.AudioFileValue

    @pytest.mark.parametrize(
        "file_name", ["test.pdf", "test.doc", "test.docx", "test.xls", "test.xlsx", "test.ppt", "test.pptx"]
    )
    def test_document(self, file_name: str) -> None:
        result = _get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.DocumentFileValue

    def test_moving_image(self) -> None:
        result = _get_file_type_info("test.mp4")
        assert result.knora_type == KNORA_API.MovingImageFileValue

    @pytest.mark.parametrize(
        "file_name", ["test.jpg", "test.jpeg", "test.jp2", "test.png", "test.tif", "test.tiff", "test.jpx"]
    )
    def test_still_image(self, file_name: str) -> None:
        result = _get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.StillImageFileValue

    @pytest.mark.parametrize(
        "file_name", ["test.odd", "test.rng", "test.txt", "test.xml", "test.xsd", "test.xsl", "test.csv"]
    )
    def test_text(self, file_name: str) -> None:
        result = _get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.TextFileValue

    @pytest.mark.parametrize(("file_name", "ending"), [("test.", ""), ("test", ""), ("test.other", "other")])
    def test_raises(self, file_name: str, ending: str) -> None:
        msg = regex.escape(f"Unknown file ending '{ending}' for file '{file_name}'")
        with pytest.raises(BaseError, match=msg):
            _get_file_type_info(file_name)


class TestMakeMetadata:
    def test_permissions(self) -> None:
        bn = BNode()
        meta = FileValueMetadata("permissions")
        g = _add_metadata(bn, meta)
        assert len(g) == 1
        permission = next(g.objects(bn, KNORA_API.hasPermissions))
        assert permission == Literal("permissions", datatype=XSD.string)

    def test_no_permissions(self) -> None:
        bn = BNode()
        meta = FileValueMetadata(None)
        g = _add_metadata(bn, meta)
        assert len(g) == 0
