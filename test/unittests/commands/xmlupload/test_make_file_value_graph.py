from typing import cast

import pytest
import regex
from lxml import etree
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.make_file_value_graph import _add_metadata
from dsp_tools.commands.xmlupload.make_file_value_graph import _get_file_type_info
from dsp_tools.commands.xmlupload.make_file_value_graph import _make_file_value_graph
from dsp_tools.commands.xmlupload.make_file_value_graph import make_iiif_uri_value_graph
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import ARCHIVE_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import AUDIO_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import DOCUMENT_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import MOVING_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import STILL_IMAGE_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import TEXT_FILE_VALUE
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import AbstractFileValue
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import FileValueMetadata
from dsp_tools.commands.xmlupload.models.serialise.abstract_file_value import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import PermissionNotExistsError

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@pytest.fixture
def metadata_permissions() -> FileValueMetadata:
    return FileValueMetadata("permissions")


@pytest.fixture
def metadata_no_permissions() -> FileValueMetadata:
    return FileValueMetadata(None)


@pytest.fixture
def abstract_file_permissions(metadata_permissions: FileValueMetadata) -> AbstractFileValue:
    return AbstractFileValue("IdFromIngest", metadata_permissions)


@pytest.fixture
def abstract_file_no_permissions(metadata_no_permissions: FileValueMetadata) -> AbstractFileValue:
    return AbstractFileValue("IdFromIngest", metadata_no_permissions)


class TestIIIFURI:
    def test_make_iiif_uri_value_graph_with_permissions(self) -> None:
        permission = {"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})}
        url = "http://example.org/prefix1/abcd1234/full/full/0/native.jpg"
        xml_str = f"""
            <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
                <iiif-uri permissions="open">{url}</iiif-uri>
            </resource>
            """
        xmlresource = XMLResource.from_node(etree.fromstring(xml_str), "foo")
        test_val = cast(IIIFUriInfo, xmlresource.iiif_uri)
        res_bn = BNode()
        g, _ = make_iiif_uri_value_graph(test_val, res_bn, permission)
        assert len(g) == 4
        val_bn = next(g.objects(res_bn, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(val_bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        assert next(g.objects(val_bn, KNORA_API.fileValueHasExternalUrl)) == Literal(url, datatype=XSD.string)
        assert next(g.objects(val_bn, KNORA_API.hasPermissions)) == Literal(
            "CR knora-admin:ProjectAdmin", datatype=XSD.string
        )

    def test_make_iiif_uri_value_graph_no_permissions(self) -> None:
        permission = {"open": Permissions()}
        url = "http://example.org/prefix1/abcd1234/full/full/0/native.jpg"
        xml_str = f"""
            <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
                <iiif-uri>{url}</iiif-uri>
            </resource>
            """
        xmlresource = XMLResource.from_node(etree.fromstring(xml_str), "foo")
        test_val = cast(IIIFUriInfo, xmlresource.iiif_uri)
        res_bn = BNode()
        g, _ = make_iiif_uri_value_graph(test_val, res_bn, permission)
        assert len(g) == 3
        val_bn = next(g.objects(res_bn, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(val_bn, RDF.type)) == KNORA_API.StillImageExternalFileValue
        assert next(g.objects(val_bn, KNORA_API.fileValueHasExternalUrl)) == Literal(url, datatype=XSD.string)

    def test_make_iiif_uri_value_graph_raises(self) -> None:
        permission = {"": Permissions()}
        xml_str = """
            <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
                <iiif-uri permissions="open">http://example.org/prefix1/abcd1234/full/full/0/native.jpg</iiif-uri>
            </resource>
            """
        xmlresource = XMLResource.from_node(etree.fromstring(xml_str), "foo")
        test_val = cast(IIIFUriInfo, xmlresource.iiif_uri)
        with pytest.raises(PermissionNotExistsError):
            make_iiif_uri_value_graph(test_val, BNode(), permission)


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
    def test_with_permissions(self, abstract_file_permissions: AbstractFileValue, type_info: RDFPropTypeInfo) -> None:
        res_bn = BNode()
        g = _make_file_value_graph(abstract_file_permissions, type_info, res_bn)
        assert len(g) == 4
        val_bn = next(g.objects(res_bn, type_info.knora_prop))
        assert next(g.objects(val_bn, RDF.type)) == type_info.knora_type
        filename = next(g.objects(val_bn, KNORA_API.fileValueHasFilename))
        assert filename == Literal("IdFromIngest", datatype=XSD.string)
        permissions = next(g.objects(val_bn, KNORA_API.hasPermissions))
        assert permissions == Literal("permissions", datatype=XSD.string)

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
    def test_no_permissions(self, abstract_file_no_permissions: AbstractFileValue, type_info: RDFPropTypeInfo) -> None:
        res_bn = BNode()
        g = _make_file_value_graph(abstract_file_no_permissions, type_info, res_bn)
        assert len(g) == 3
        val_bn = next(g.objects(res_bn, type_info.knora_prop))
        assert next(g.objects(val_bn, RDF.type)) == type_info.knora_type
        filename = next(g.objects(val_bn, KNORA_API.fileValueHasFilename))
        assert filename == Literal("IdFromIngest", datatype=XSD.string)


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
    def test_permissions(self, metadata_permissions: FileValueMetadata) -> None:
        bn = BNode()
        g = _add_metadata(bn, metadata_permissions)
        assert len(g) == 1
        permission = next(g.objects(bn, KNORA_API.hasPermissions))
        assert permission == Literal("permissions", datatype=XSD.string)

    def test_no_permissions(self, metadata_no_permissions: FileValueMetadata) -> None:
        bn = BNode()
        g = _add_metadata(bn, metadata_no_permissions)
        assert len(g) == 0
