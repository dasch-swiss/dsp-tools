# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
import regex
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.make_rdf_graph.constants import ARCHIVE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import AUDIO_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DOCUMENT_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import MOVING_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import STILL_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TEXT_FILE_VALUE
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import _add_metadata
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import _make_abstract_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import get_file_type_info
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_file_value_graph
from dsp_tools.commands.xmlupload.make_rdf_graph.make_file_value import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.rdf_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.rdf_models import FileValueMetadata
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.rdflib_constants import KNORA_API


@pytest.fixture
def metadata_with_permissions_no_legal_info() -> FileValueMetadata:
    return FileValueMetadata(None, None, None, "CR knora-admin:ProjectAdmin")


@pytest.fixture
def metadata_no_permissions_no_legal_info() -> FileValueMetadata:
    return FileValueMetadata(None, None, None, None)


@pytest.fixture
def metadata_with_legal_info() -> FileValueMetadata:
    return FileValueMetadata("https://iri.ch", "copy", ["auth1", "auth2"], None)


@pytest.fixture
def abstract_file_with_permissions(metadata_with_permissions_no_legal_info) -> AbstractFileValue:
    return AbstractFileValue("value", metadata_with_permissions_no_legal_info)


@pytest.fixture
def abstract_file_no_permissions(metadata_no_permissions_no_legal_info) -> AbstractFileValue:
    return AbstractFileValue("value", metadata_no_permissions_no_legal_info)


class TestIIIFURI:
    def test_make_iiif_uri_value_graph_with_permissions(self, abstract_file_with_permissions):
        res_bn = BNode()
        g = make_iiif_uri_value_graph(abstract_file_with_permissions, res_bn)
        assert len(g) == 4
        val_bn = next(g.objects(res_bn, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(val_bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        value = next(g.objects(val_bn, KNORA_API.stillImageFileValueHasExternalUrl))
        assert value == Literal("value", datatype=XSD.string)
        permissions = next(g.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)

    def test_make_iiif_uri_value_graph_no_permissions(self, abstract_file_no_permissions):
        res_bn = BNode()
        g = make_iiif_uri_value_graph(abstract_file_no_permissions, res_bn)
        assert len(g) == 3
        val_bn = next(g.objects(res_bn, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(val_bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        value = next(g.objects(val_bn, KNORA_API.stillImageFileValueHasExternalUrl))
        assert value == Literal("value", datatype=XSD.string)


class TestMakeBitstreamFileGraph:
    def test_make_file_value_graph_with_permissions(self, metadata_with_permissions_no_legal_info):
        bitstream = BitstreamInfo(
            local_file="path/test.txt",
            internal_file_name="FileID",
            permissions=Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]}),
        )
        res_bn = BNode()
        g = make_file_value_graph(bitstream, metadata_with_permissions_no_legal_info, res_bn)
        file_bn = next(g.objects(res_bn, KNORA_API.hasTextFileValue))
        assert next(g.objects(file_bn, RDF.type)) == KNORA_API.TextFileValue
        file_id = next(g.objects(file_bn, KNORA_API.fileValueHasFilename))
        assert file_id == Literal("FileID", datatype=XSD.string)
        permissions = next(g.objects(file_bn, KNORA_API.hasPermissions))
        assert permissions == Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)

    def test_make_file_value_graph_no_permissions(self, metadata_with_permissions_no_legal_info):
        bitstream = BitstreamInfo(
            local_file="path/test.txt",
            internal_file_name="FileID",
            permissions=None,
        )
        res_bn = BNode()
        g = make_file_value_graph(bitstream, metadata_with_permissions_no_legal_info, res_bn)
        file_bn = next(g.objects(res_bn, KNORA_API.hasTextFileValue))
        assert next(g.objects(file_bn, RDF.type)) == KNORA_API.TextFileValue
        file_id = next(g.objects(file_bn, KNORA_API.fileValueHasFilename))
        assert file_id == Literal("FileID", datatype=XSD.string)


class TestMakeFileValueGraph:
    @pytest.mark.parametrize(
        "type_info",
        [
            ARCHIVE_FILE_VALUE,
            AUDIO_FILE_VALUE,
            DOCUMENT_FILE_VALUE,
            MOVING_IMAGE_FILE_VALUE,
            STILL_IMAGE_FILE_VALUE,
            TEXT_FILE_VALUE,
        ],
    )
    def test_with_permissions(self, abstract_file_with_permissions, type_info):
        res_bn = BNode()
        g = _make_abstract_file_value_graph(abstract_file_with_permissions, type_info, res_bn)
        assert len(g) == 4
        val_bn = next(g.objects(res_bn, type_info.knora_prop))
        assert next(g.objects(val_bn, RDF.type)) == type_info.knora_type
        filename = next(g.objects(val_bn, KNORA_API.fileValueHasFilename))
        assert filename == Literal("value", datatype=XSD.string)
        permissions = next(g.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)

    @pytest.mark.parametrize(
        "type_info",
        [
            ARCHIVE_FILE_VALUE,
            AUDIO_FILE_VALUE,
            DOCUMENT_FILE_VALUE,
            MOVING_IMAGE_FILE_VALUE,
            STILL_IMAGE_FILE_VALUE,
            TEXT_FILE_VALUE,
        ],
    )
    def test_no_permissions(self, abstract_file_no_permissions, type_info):
        res_bn = BNode()
        g = _make_abstract_file_value_graph(abstract_file_no_permissions, type_info, res_bn)
        assert len(g) == 3
        val_bn = next(g.objects(res_bn, type_info.knora_prop))
        assert next(g.objects(val_bn, RDF.type)) == type_info.knora_type
        filename = next(g.objects(val_bn, KNORA_API.fileValueHasFilename))
        assert filename == Literal("value", datatype=XSD.string)


class TestFileTypeInfo:
    @pytest.mark.parametrize(
        "file_name", ["test.zip", "test.tar", "test.gz", "test.z", "test.tgz", "test.gzip", "test.7z"]
    )
    def test_archive(self, file_name: str):
        result = get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.ArchiveFileValue

    @pytest.mark.parametrize("file_name", ["test.mp3", "test.wav"])
    def test_audio(self, file_name: str):
        result = get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.AudioFileValue

    @pytest.mark.parametrize(
        "file_name", ["test.pdf", "test.doc", "test.docx", "test.xls", "test.xlsx", "test.ppt", "test.pptx"]
    )
    def test_document(self, file_name: str):
        result = get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.DocumentFileValue

    def test_moving_image(self):
        result = get_file_type_info("test.mp4")
        assert result.knora_type == KNORA_API.MovingImageFileValue

    @pytest.mark.parametrize(
        "file_name", ["test.jpg", "test.jpeg", "path/test.jp2", "test.png", "test.tif", "test.tiff", "test.jpx"]
    )
    def test_still_image(self, file_name: str):
        result = get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.StillImageFileValue

    @pytest.mark.parametrize(
        "file_name",
        ["path/test.odd", "test.rng", "test.txt", "test.xml", "test.xsd", "test.xsl", "test.csv", "test.json"],
    )
    def test_text(self, file_name: str):
        result = get_file_type_info(file_name)
        assert result.knora_type == KNORA_API.TextFileValue

    @pytest.mark.parametrize(("file_name", "ending"), [("test.", ""), ("test", ""), ("test.other", "other")])
    def test_raises(self, file_name: str, ending: str):
        msg = regex.escape(f"Unknown file ending '{ending}' for file '{file_name}'")
        with pytest.raises(BaseError, match=msg):
            get_file_type_info(file_name)


class TestAddMetadata:
    def test_permissions(self, metadata_with_permissions_no_legal_info):
        bn = BNode()
        g = _add_metadata(bn, metadata_with_permissions_no_legal_info)
        assert len(g) == 1
        permission = next(g.objects(bn, KNORA_API.hasPermissions))
        assert permission == Literal("CR knora-admin:ProjectAdmin", datatype=XSD.string)

    def test_metadata_with_legal_info(self, metadata_with_legal_info):
        bn = BNode()
        g = _add_metadata(bn, metadata_with_legal_info)
        assert len(g) == 4
        license_iri = next(g.objects(bn, KNORA_API.hasLicense))
        assert license_iri == URIRef("https://iri.ch")
        copyright_str = next(g.objects(bn, KNORA_API.hasCopyrightHolder))
        assert copyright_str == Literal("copy", datatype=XSD.string)
        auth_set = set(g.objects(bn, KNORA_API.hasAuthorship))
        expected_auth = {Literal("auth1", datatype=XSD.string), Literal("auth2", datatype=XSD.string)}
        assert auth_set == expected_auth

    def test_no_permissions(self, metadata_no_permissions_no_legal_info):
        bn = BNode()
        g = _add_metadata(bn, metadata_no_permissions_no_legal_info)
        assert len(g) == 0
