import warnings
from typing import Any

import numpy as np
import pandas as pd
import polars as pl
import pytest

from dsp_tools.xmllib.internal.constants import KNOWN_XML_TAGS
from dsp_tools.xmllib.value_checkers import check_richtext_syntax
from dsp_tools.xmllib.value_checkers import is_bool_like
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_date
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_dsp_ark
from dsp_tools.xmllib.value_checkers import is_dsp_iri
from dsp_tools.xmllib.value_checkers import is_geoname
from dsp_tools.xmllib.value_checkers import is_integer
from dsp_tools.xmllib.value_checkers import is_nonempty_value
from dsp_tools.xmllib.value_checkers import is_timestamp


@pytest.mark.parametrize(
    "text",
    [
        "None",
        "a",
        "-",
        0,
        1,
        "0",
        "1",
        True,
        False,
        "עִבְרִית",
        "اَلْعَرَبِيَّةُ",
    ],
)
def test_is_nonempty_value_correct(text: str) -> None:
    assert is_nonempty_value(text)


@pytest.mark.parametrize(
    "text",
    [
        np.nan,
        pd.NA,
        None,
        "",
        " ",
        " \t ",
        " \n ",
        " \r ",
        " \v ",  # vertical tab
        " \f ",
        " \u00a0 ",  # non-breaking space
        " \u200b ",  # zero-width space
        " \ufeff ",  # Zero-Width No-Break Space
        " \t\n\r\v\f \u00a0 \u200b \ufeff",
    ],
)
def test_is_nonempty_value_wrong(text: str) -> None:
    assert not is_nonempty_value(text)


def test_is_nonempty_value_wrong_polars_types() -> None:
    df = pl.DataFrame({"col": [float("nan"), np.nan, None]})
    for row in df.iter_rows(named=True):
        assert not is_nonempty_value(row["col"])


@pytest.mark.parametrize(
    "val", ["false", "0", "0.0", "no", "true", "1", "1.0", "yes", False, True, "oui", "JA", "non", "nein"]
)
def test_is_bool_correct(val: Any) -> None:
    assert is_bool_like(val)


@pytest.mark.parametrize("val", ["none", "asdfioh", None, pd.NA])
def test_is_bool_wrong(val: Any) -> None:
    assert not is_bool_like(val)


@pytest.mark.parametrize("val", ["#234567", "#abcdef", "#123abc"])
def test_is_color_correct(val: str) -> None:
    assert is_color(val)


@pytest.mark.parametrize("val", [12334, "123abc", "234567#"])
def test_is_color_wrong(val: Any) -> None:
    assert not is_color(val)


@pytest.mark.parametrize(
    "val",
    [
        "GREGORIAN:CE:0476-09-04:CE:0476-09-04",
        "GREGORIAN:BC:2000:BC:1000",
        "JULIAN:CE:0476-09-04:CE:0476-09-04",
        "JULIAN:BC:2000:BC:1000",
        "ISLAMIC:0476-09-04:0476-09-04",
        "ISLAMIC:1000:2000",
        "GREGORIAN:0476-09-04:0476-09-04",
        "CE:0476-09-04:CE:0476-09-04",
    ],
)
def test_is_date_correct(val: str) -> None:
    assert is_date(val)


@pytest.mark.parametrize(
    "val",
    [
        "OTHER:BC:2000:BC:1000",
        "GREGORIAN:other:2000:other:1000",
        "GREGORIAN::CE:0476-09-04:CE:0476-09-04",
        "GREGORIAN:CE:0476-09-04:CE::0476-09-04",
        "GREGORIAN:CE:0476-09-04::CE:0476-09-04",
        "GREGORIAN:CE::0476-09-04:CE:0476-09-04",
        "ISLAMIC:BC:0476-09-04:BC:0476-09-04",
        "ISLAMIC:BCE:0476-09-04:BCE:0476-09-04",
        "ISLAMIC:CE:0476-09-04:CE:0476-09-04",
        "ISLAMIC:AD:0476-09-04:AD:0476-09-04",
        "ISLAMIC:AH:0476-09-04:AH:0476-09-04",  # Anno Hegirae is not implemented yet
        "ISLAMIC:BH:0476-09-04:BH:0476-09-04",  # Before Hijra is not implemented yet
        "ISLAMIC:AH:0476-09-04:0476-09-04",
        "ISLAMIC:0476-09-04:AH:0476-09-04",
    ],
)
def test_is_date_wrong(val: Any) -> None:
    assert not is_date(val)


@pytest.mark.parametrize("val", ["00001", 23412])
def test_is_geoname_correct(val: Any) -> None:
    assert is_geoname(val)


@pytest.mark.parametrize("val", [122.2, "asdf"])
def test_is_geoname_wrong(val: Any) -> None:
    assert not is_geoname(val)


@pytest.mark.parametrize("val", [1.2, "1.432", 1, "1", -1.1, "1e-1", "1e2"])
def test_is_decimal_correct(val: Any) -> None:
    assert is_decimal(val)


@pytest.mark.parametrize("val", ["asf", np.nan, pd.NA, True, False])
def test_is_decimal_wrong(val: Any) -> None:
    assert not is_decimal(val)


@pytest.mark.parametrize("val", [1, "1", -1])
def test_is_integer_correct(val: Any) -> None:
    assert is_integer(val)


@pytest.mark.parametrize("val", [1.2, "1.2", "wdasd", True, False, "1e2"])
def test_is_integer_wrong(val: Any) -> None:
    assert not is_integer(val)


@pytest.mark.parametrize(
    "val",
    [
        "2019-10-23T13:45:12.01-14:00",
        "2019-10-23T13:45:12-14:00",
        "2019-10-23T13:45:12Z",
        "2019-10-23T13:45:12-13:30",
        "2019-10-23T13:45:12+01:00",
        "2019-10-23T13:45:12.1111111+01:00",
        "2019-10-23T13:45:12.123456789012Z",
    ],
)
def test_is_timestamp_correct(val: Any) -> None:
    assert is_timestamp(val)


@pytest.mark.parametrize(
    "val",
    [
        True,
        10.0,
        5,
        "2019-10-2",
        "CE:1849:CE:1850",
        "2019-10-23T13:45:12.1234567890123Z",
        "2022",
        "GREGORIAN:CE:2014-01-31",
    ],
)
def test_is_timestamp_wrong(val: Any) -> None:
    assert not is_timestamp(val)


@pytest.mark.parametrize("val", ["http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"])
def test_is_dsp_iri_correct(val: Any) -> None:
    assert is_dsp_iri(val)


@pytest.mark.parametrize("val", ["http://www.example.org/prefix1/", "ark:/72163/4123-43xc6ivb931-a.2022829"])
def test_is_dsp_iri_wrong(val: Any) -> None:
    assert not is_dsp_iri(val)


@pytest.mark.parametrize("val", ["ark:/72163/4123-43xc6ivb931-a.2022829"])
def test_is_dsp_ark_correct(val: Any) -> None:
    assert is_dsp_ark(val)


@pytest.mark.parametrize("val", ["http://www.example.org/prefix1/", "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"])
def test_is_dsp_ark_wrong(val: Any) -> None:
    assert not is_dsp_ark(val)


@pytest.mark.parametrize(
    "val",
    [f"Start Text<{tag}> middle text </{tag}> ending." for tag in KNOWN_XML_TAGS],
)
def test_check_richtext_syntax_correct(val: Any) -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        check_richtext_syntax(val)
    assert len(caught_warnings) == 0


@pytest.mark.parametrize(
    "val",
    [
        'Start <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a> ending.',
        '<footnote content="footnote text"/>',
    ],
)
def test_check_richtext_syntax_correct_special_cases(val: Any) -> None:
    with warnings.catch_warnings(record=True) as caught_warnings:
        check_richtext_syntax(val)
    assert len(caught_warnings) == 0


if __name__ == "__main__":
    pytest.main([__file__])
