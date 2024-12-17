import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.validate_data.make_data_rdf import _get_file_extension
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_resource
from dsp_tools.commands.validate_data.make_data_rdf import _make_one_value
from dsp_tools.commands.validate_data.make_data_rdf import _transform_file_value
from dsp_tools.commands.validate_data.models.data_deserialised import BitstreamDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import UriValueDeserialised
from dsp_tools.commands.validate_data.models.data_rdf import FileValueRDF
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO

RES_IRI = DATA["id"]


class TestResource:
    def test_empty(self, resource_deserialised_no_values: ResourceDeserialised) -> None:
        res_g = _make_one_resource(resource_deserialised_no_values)
        assert len(res_g) == 2
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)

    def test_with_props(self, resource_deserialised_with_values: ResourceDeserialised) -> None:
        res_g = _make_one_resource(resource_deserialised_with_values)
        assert len(res_g) == 5
        assert next(res_g.objects(RES_IRI, RDF.type)) == ONTO.ClassWithEverything
        assert next(res_g.objects(RES_IRI, RDFS.label)) == Literal("lbl", datatype=XSD.string)
        bool_bn = next(res_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(res_g.objects(bool_bn, KNORA_API.booleanValueAsBoolean)) == Literal(False, datatype=XSD.boolean)


class TestBooleanValue:
    def test_corr(self, boolean_value_deserialised_corr: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_one(self, boolean_value_deserialised_one: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_one, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("true", datatype=XSD.boolean)

    def test_zero(self, boolean_value_deserialised_zero: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_zero, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("false", datatype=XSD.boolean)

    def test_none(self, boolean_value_deserialised_none: BooleanValueDeserialised) -> None:
        val_g = _make_one_value(boolean_value_deserialised_none, RES_IRI)
        bn = next(val_g.objects(RES_IRI, ONTO.testBoolean))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.BooleanValue
        assert next(val_g.objects(bn, KNORA_API.booleanValueAsBoolean)) == Literal("", datatype=XSD.string)


class TestColorValue:
    def test_corr(self, color_value_deserialised_corr: ColorValueDeserialised) -> None:
        val_g = _make_one_value(color_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("#00ff00", datatype=XSD.string)

    def test_none(self, color_value_deserialised_none: ColorValueDeserialised) -> None:
        val_g = _make_one_value(color_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testColor))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ColorValue
        assert next(val_g.objects(bn, KNORA_API.colorValueAsColor)) == Literal("", datatype=XSD.string)


class TestDateValue:
    def test_corr(self, date_value_deserialised_corr: DateValueDeserialised) -> None:
        val_g = _make_one_value(date_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal(
            "JULIAN:BCE:0700:BCE:0600", datatype=XSD.string
        )

    def test_none(self, date_value_deserialised_none: DateValueDeserialised) -> None:
        val_g = _make_one_value(date_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testSubDate1))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DateValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("", datatype=XSD.string)


class TestDecimalValue:
    def test_corr(self, decimal_value_deserialised_corr: DecimalValueDeserialised) -> None:
        val_g = _make_one_value(decimal_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("1.2", datatype=XSD.decimal)

    def test_none(self, decimal_value_deserialised_none: DecimalValueDeserialised) -> None:
        val_g = _make_one_value(decimal_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testDecimalSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.DecimalValue
        assert next(val_g.objects(bn, KNORA_API.decimalValueAsDecimal)) == Literal("", datatype=XSD.string)


class TestGeonameValue:
    def test_corr(self, geoname_value_deserialised_corr: GeonameValueDeserialised) -> None:
        val_g = _make_one_value(geoname_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("1241345", datatype=XSD.string)

    def test_none(self, geoname_value_deserialised_none: GeonameValueDeserialised) -> None:
        val_g = _make_one_value(geoname_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testGeoname))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.GeonameValue
        assert next(val_g.objects(bn, KNORA_API.geonameValueAsGeonameCode)) == Literal("", datatype=XSD.string)


class TestIntValue:
    def test_corr(self, int_value_deserialised_corr: IntValueDeserialised) -> None:
        val_g = _make_one_value(int_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("1", datatype=XSD.integer)

    def test_none(self, int_value_deserialised_none: IntValueDeserialised) -> None:
        val_g = _make_one_value(int_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testIntegerSimpleText))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.IntValue
        assert next(val_g.objects(bn, KNORA_API.intValueAsInt)) == Literal("", datatype=XSD.string)


class TestLinkValue:
    def test_corr(self, link_value_deserialised_corr: LinkValueDeserialised) -> None:
        val_g = _make_one_value(link_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA["link-id"]

    def test_none(self, link_value_deserialised_none: LinkValueDeserialised) -> None:
        val_g = _make_one_value(link_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testHasLinkTo))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.LinkValue
        assert next(val_g.objects(bn, API_SHAPES.linkValueHasTargetID)) == DATA[""]


class TestListValue:
    def test_corr(self, list_value_deserialised_corr: ListValueDeserialised) -> None:
        val_g = _make_one_value(list_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, API_SHAPES.listNodeAsString)) == Literal("n1", datatype=XSD.string)
        assert next(val_g.objects(bn, API_SHAPES.listNameAsString)) == Literal("firstList", datatype=XSD.string)

    def test_none(self, list_value_deserialised_none: ListValueDeserialised) -> None:
        val_g = _make_one_value(list_value_deserialised_none, RES_IRI)
        assert len(val_g) == 4
        bn = next(val_g.objects(RES_IRI, ONTO.testListProp))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.ListValue
        assert next(val_g.objects(bn, API_SHAPES.listNodeAsString)) == Literal("", datatype=XSD.string)
        assert next(val_g.objects(bn, API_SHAPES.listNameAsString)) == Literal("firstList", datatype=XSD.string)


class TestSimpleTextValue:
    def test_corr(self, simple_text_deserialised_corr: SimpleTextDeserialised) -> None:
        val_g = _make_one_value(simple_text_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("simple text", datatype=XSD.string)

    def test_none(self, simple_text_deserialised_none: SimpleTextDeserialised) -> None:
        val_g = _make_one_value(simple_text_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTextarea))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.valueAsString)) == Literal("", datatype=XSD.string)


class TestRichtextValue:
    def test_corr(self, richtext_deserialised_corr: RichtextDeserialised) -> None:
        val_g = _make_one_value(richtext_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("rich text", datatype=XSD.string)

    def test_none(self, richtext_deserialised_none: RichtextDeserialised) -> None:
        val_g = _make_one_value(richtext_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testRichtext))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TextValue
        assert next(val_g.objects(bn, KNORA_API.textValueAsXml)) == Literal("", datatype=XSD.string)


class TestTimeValue:
    def test_corr(self, time_value_deserialised_corr: TimeValueDeserialised) -> None:
        val_g = _make_one_value(time_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal(
            "2019-10-23T13:45:12.01-14:00", datatype=XSD.dateTimeStamp
        )

    def test_none(self, time_value_deserialised_none: TimeValueDeserialised) -> None:
        val_g = _make_one_value(time_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testTimeValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.TimeValue
        assert next(val_g.objects(bn, KNORA_API.timeValueAsTimeStamp)) == Literal("", datatype=XSD.string)


class TestUriValue:
    def test_corr(self, uri_value_deserialised_corr: UriValueDeserialised) -> None:
        val_g = _make_one_value(uri_value_deserialised_corr, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("https://dasch.swiss", datatype=XSD.anyURI)

    def test_none(self, uri_value_deserialised_none: UriValueDeserialised) -> None:
        val_g = _make_one_value(uri_value_deserialised_none, RES_IRI)
        assert len(val_g) == 3
        bn = next(val_g.objects(RES_IRI, ONTO.testUriValue))
        assert next(val_g.objects(bn, RDF.type)) == KNORA_API.UriValue
        assert next(val_g.objects(bn, KNORA_API.uriValueAsUri)) == Literal("", datatype=XSD.string)


class TestTransformFileValue:
    @pytest.mark.parametrize("extension", ["zip", "tar", "gz", "z", "tgz", "gzip", "7z"])
    def test_archive_file(self, extension: str) -> None:
        bitstream = BitstreamDeserialised("id", f"test.{extension}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.ArchiveFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)
        bitstream = BitstreamDeserialised("id", f"test.{extension.upper()}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.ArchiveFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    @pytest.mark.parametrize("extension", ["mp3", "wav"])
    def test_audio_file(self, extension: str) -> None:
        bitstream = BitstreamDeserialised("id", f"test.{extension}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.AudioFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)
        bitstream = BitstreamDeserialised("id", f"test.{extension.upper()}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.AudioFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    @pytest.mark.parametrize("extension", ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx"])
    def test_document_file(self, extension: str) -> None:
        bitstream = BitstreamDeserialised("id", f"test.{extension}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.DocumentFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)
        bitstream = BitstreamDeserialised("id", f"test.{extension.upper()}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.DocumentFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    def test_moving_image(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.mp4")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.MovingImageFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    @pytest.mark.parametrize("extension", ["jpg", "jpeg", "png", "tif", "tiff", "jp2"])
    def test_still_image_file(self, extension: str) -> None:
        bitstream = BitstreamDeserialised("id", f"test.{extension}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.StillImageFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)
        bitstream = BitstreamDeserialised("id", f"test.{extension.upper()}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.StillImageFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    def test_still_image_iiif(self) -> None:
        iiif = IIIFUriDeserialised(
            "id", "https://iiif.wellcomecollection.org/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg"
        )
        result = _transform_file_value(iiif)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.StillImageExternalFileValue
        assert result.value == Literal(iiif.value, datatype=XSD.anyURI)

    @pytest.mark.parametrize("extension", ["odd", "rng", "txt", "xml", "xsd", "xsl", "csv", "json"])
    def test_text_file(self, extension: str) -> None:
        bitstream = BitstreamDeserialised("id", f"test.{extension}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.TextFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)
        bitstream = BitstreamDeserialised("id", f"test.{extension.upper()}")
        result = _transform_file_value(bitstream)
        assert isinstance(result, FileValueRDF)
        assert result.prop_type_info.knora_type == KNORA_API.TextFileValue
        assert result.value == Literal(bitstream.value, datatype=XSD.string)

    def test_other(self) -> None:
        bitstream = BitstreamDeserialised("id", "test.other")
        result = _transform_file_value(bitstream)
        assert not result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("test.jpg", "jpg"),
        ("test.JPG", "jpg"),
        (None, ""),
        ("test", ""),
    ],
)
def test_get_file_extension(value: str | None, expected: str) -> None:
    assert _get_file_extension(value) == expected


if __name__ == "__main__":
    pytest.main([__file__])
