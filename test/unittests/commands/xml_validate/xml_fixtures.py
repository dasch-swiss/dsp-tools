import pytest
from lxml import etree


@pytest.fixture
def boolean_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def boolean_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def color_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def color_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def date_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def date_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def decimal_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def decimal_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def geometry_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def geometry_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def geoname_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def geoname_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def list_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def list_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def integer_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def integer_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def resptr_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def resptr_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def text_richtext_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def text_richtext_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def text_simpletext_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def text_simpletext_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def time_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def time_value_wrong() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def uri_value_corr() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def uri_value_wrong() -> etree._Element:
    return etree.fromstring("""""")
