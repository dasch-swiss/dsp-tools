import pytest

from dsp_tools.commands.xml_validate.models.data_deserialised import BooleanValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ColorValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import DateValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import DecimalValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import GeonameValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import IntValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import RichtextDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import TimeValueDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import UriValueDeserialised


@pytest.fixture
def resource_deserialised_with_values(boolean_value_deserialised: BooleanValueDeserialised) -> ResourceDeserialised:
    return ResourceDeserialised(
        "id", "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything", "lbl", [boolean_value_deserialised]
    )


@pytest.fixture
def deserialised_no_values() -> ResourceDeserialised:
    return ResourceDeserialised("id", "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything", "lbl", [])


@pytest.fixture
def boolean_value_deserialised_corr() -> BooleanValueDeserialised:
    return BooleanValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "false")


@pytest.fixture
def boolean_value_deserialised_none() -> BooleanValueDeserialised:
    return BooleanValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def color_value_deserialised_corr() -> ColorValueDeserialised:
    return ColorValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "00ff00")


@pytest.fixture
def color_value_deserialised_none() -> ColorValueDeserialised:
    return ColorValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def date_value_deserialised_corr() -> DateValueDeserialised:
    return DateValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "JULIAN:BCE:0700:BCE:0600")


@pytest.fixture
def date_value_deserialised_none() -> DateValueDeserialised:
    return DateValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def decimal_value_deserialised_corr() -> DecimalValueDeserialised:
    return DecimalValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "1.2")


@pytest.fixture
def decimal_value_deserialised_none() -> DecimalValueDeserialised:
    return DecimalValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def geoname_value_deserialised_corr() -> GeonameValueDeserialised:
    return GeonameValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "1241345")


@pytest.fixture
def geoname_value_deserialised_none() -> GeonameValueDeserialised:
    return GeonameValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def int_value_deserialised_corr() -> IntValueDeserialised:
    return IntValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "1")


@pytest.fixture
def int_value_deserialised_none() -> IntValueDeserialised:
    return IntValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def link_value_deserialised_corr() -> LinkValueDeserialised:
    return LinkValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "link-id")


@pytest.fixture
def link_value_deserialised_none() -> LinkValueDeserialised:
    return LinkValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def list_value_deserialised_corr() -> ListValueDeserialised:
    return ListValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "n1", "onlyList")


@pytest.fixture
def list_value_deserialised_none() -> ListValueDeserialised:
    return ListValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None, "onlyList")


@pytest.fixture
def simple_text_deserialised_corr() -> SimpleTextDeserialised:
    return SimpleTextDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "simple text")


@pytest.fixture
def simple_text_deserialised_none() -> SimpleTextDeserialised:
    return SimpleTextDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def richtext_deserialised_corr() -> RichtextDeserialised:
    return RichtextDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "rich text")


@pytest.fixture
def richtext_deserialised_none() -> RichtextDeserialised:
    return RichtextDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def time_value_deserialised_corr() -> TimeValueDeserialised:
    return TimeValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "2019-10-23T13:45:12.01-14:00")


@pytest.fixture
def time_value_deserialised_none() -> TimeValueDeserialised:
    return TimeValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)


@pytest.fixture
def uri_value_deserialised_corr() -> UriValueDeserialised:
    return UriValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", "https://dasch.swiss")


@pytest.fixture
def uri_value_deserialised_none() -> UriValueDeserialised:
    return UriValueDeserialised("http://0.0.0.0:3333/ontology/9999/onto/v2#", None)
