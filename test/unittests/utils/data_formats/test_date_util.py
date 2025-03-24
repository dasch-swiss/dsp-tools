import pytest

from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.data_formats.date_util import Calendar
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.data_formats.date_util import Era
from dsp_tools.utils.data_formats.date_util import SingleDate
from dsp_tools.utils.data_formats.date_util import _parse_single_date
from dsp_tools.utils.data_formats.date_util import _split_date_string
from dsp_tools.utils.data_formats.date_util import parse_date_string


class TestParseDateStringWithDateOnly:
    """Tests parsing a date string with only dates, no era or calendar information."""

    def test_start_date(self) -> None:
        date_string = "2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_year(self) -> None:
        date_string = "2020"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=None, day=None)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_year_and_month(self) -> None:
        date_string = "2020-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=1, day=None)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_and_end_year(self) -> None:
        date_string = "2020:2021"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.CE, year=2020, month=None, day=None)
        expected_end = SingleDate(era=Era.CE, year=2021, month=None, day=None)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected

    def test_start_and_end_date(self) -> None:
        date_string = "2020-01-01:2021-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected_end = SingleDate(era=Era.CE, year=2021, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected


class TestParseDateStringWithEra:
    """Tests parsing a date string with era information."""

    def test_start_date_ce(self) -> None:
        date_string = "CE:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_bce(self) -> None:
        date_string = "BCE:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.BCE, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_ad(self) -> None:
        date_string = "AD:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.AD, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_bc(self) -> None:
        date_string = "BC:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.BC, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_and_end_date_ce_on_start_only(self) -> None:
        date_string = "CE:2020-01-01:2021-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected_end = SingleDate(era=Era.CE, year=2021, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected

    def test_start_and_end_date_bce_on_start_only(self) -> None:
        date_string = "BCE:2021-01-01:2020-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.BCE, year=2021, month=1, day=1)
        expected_end = SingleDate(era=Era.BCE, year=2020, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected

    def test_start_and_end_date_ce_on_both(self) -> None:
        date_string = "CE:2020-01-01:CE:2021-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected_end = SingleDate(era=Era.CE, year=2021, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected

    def test_start_and_end_date_bce_on_both(self) -> None:
        date_string = "BCE:2020-01-01:BCE:2021-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.BCE, year=2020, month=1, day=1)
        expected_end = SingleDate(era=Era.BCE, year=2021, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected

    def test_dates_across_era_border(self) -> None:
        date_string = "BCE:2020-01-01:CE:2021-02-02"
        result = parse_date_string(date_string)
        expected_start = SingleDate(era=Era.BCE, year=2020, month=1, day=1)
        expected_end = SingleDate(era=Era.CE, year=2021, month=2, day=2)
        expected = Date(Calendar.GREGORIAN, expected_start, expected_end)
        assert result == expected


class TestParseDateStringWithCalendar:
    """Tests parsing a date string with calendar information."""

    def test_start_date_gregorian(self) -> None:
        date_string = "GREGORIAN:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_gregorian_with_era(self) -> None:
        date_string = "GREGORIAN:BCE:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.BCE, year=2020, month=1, day=1)
        expected = Date(Calendar.GREGORIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_julian(self) -> None:
        date_string = "JULIAN:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        expected = Date(Calendar.JULIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_julian_with_era(self) -> None:
        date_string = "JULIAN:BCE:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=Era.BCE, year=2020, month=1, day=1)
        expected = Date(Calendar.JULIAN, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_start_date_islamic(self) -> None:
        date_string = "ISLAMIC:2020-01-01"
        result = parse_date_string(date_string)
        expected_start_and_end = SingleDate(era=None, year=2020, month=1, day=1)
        expected = Date(Calendar.ISLAMIC, expected_start_and_end, expected_start_and_end)
        assert result == expected

    def test_not_allow_islamic_calendar_with_era(self) -> None:
        date_string = "ISLAMIC:BCE:2020-01-01"
        with pytest.raises(BaseError):
            parse_date_string(date_string)


class TestSplitDateString:
    """Tests splitting a date string into its components."""

    def test_split_full_date_string(self) -> None:
        date_string = "GREGORIAN:CE:2020-01-01:CE:2021-02-02"
        result = _split_date_string(date_string)
        expected = ("GREGORIAN", "CE", "2020-01-01", "CE", "2021-02-02")
        assert result == expected

    def test_split_start_date_only(self) -> None:
        date_string = "2020-01-01"
        result = _split_date_string(date_string)
        expected = (None, None, "2020-01-01", None, None)
        assert result == expected

    def test_split_start_and_end_date_only(self) -> None:
        date_string = "2020-01-01:2021-02-02"
        result = _split_date_string(date_string)
        expected = (None, None, "2020-01-01", None, "2021-02-02")
        assert result == expected

    def test_split_start_date_with_era(self) -> None:
        date_string = "CE:2020-01-01"
        result = _split_date_string(date_string)
        expected = (None, "CE", "2020-01-01", None, None)
        assert result == expected

    def test_split_start_and_end_date_with_era(self) -> None:
        date_string = "CE:2020-01-01:CE:2021-02-02"
        result = _split_date_string(date_string)
        expected = (None, "CE", "2020-01-01", "CE", "2021-02-02")
        assert result == expected

    def test_split_start_date_with_calendar(self) -> None:
        date_string = "GREGORIAN:2020-01-01"
        result = _split_date_string(date_string)
        expected = ("GREGORIAN", None, "2020-01-01", None, None)
        assert result == expected


class TestParseSingleDate:
    """Tests parsing a single date."""

    def test_parse_date_string(self) -> None:
        date_string = "2020-01-01"
        result = _parse_single_date(date_string, Era.CE)
        expected = SingleDate(era=Era.CE, year=2020, month=1, day=1)
        assert result == expected

    def test_parse_year_only(self) -> None:
        date_string = "2020"
        result = _parse_single_date(date_string, Era.CE)
        expected = SingleDate(era=Era.CE, year=2020, month=None, day=None)
        assert result == expected

    def test_parse_year_and_month(self) -> None:
        date_string = "2020-01"
        result = _parse_single_date(date_string, Era.CE)
        expected = SingleDate(era=Era.CE, year=2020, month=1, day=None)
        assert result == expected

    def test_parse_date_fewer_digits_for_month_and_day(self) -> None:
        date_string = "0860-1-1"
        result = _parse_single_date(date_string, Era.CE)
        expected = SingleDate(era=Era.CE, year=860, month=1, day=1)
        assert result == expected

    def test_fewer_digits_in_year(self) -> None:
        date_string = "860-1-1"
        result = _parse_single_date(date_string, Era.CE)
        expected = SingleDate(era=Era.CE, year=860, month=1, day=1)
        assert result == expected

    def test_do_not_allow_more_digits_in_year(self) -> None:
        date_string = "08600-1-1"
        with pytest.raises(BaseError):
            _parse_single_date(date_string, Era.CE)

    def test_do_not_allow_more_digits_in_month(self) -> None:
        date_string = "0860-100-1"
        with pytest.raises(BaseError):
            _parse_single_date(date_string, Era.CE)

    def test_do_not_allow_more_digits_in_day(self) -> None:
        date_string = "0860-1-100"
        with pytest.raises(BaseError):
            _parse_single_date(date_string, Era.CE)

    def test_do_not_allow_non_date_string(self) -> None:
        date_string = "hello"
        with pytest.raises(BaseError):
            _parse_single_date(date_string, Era.CE)

    def test_do_not_allow_different_date_formats(self) -> None:
        date_string = "01.01.2020"
        with pytest.raises(BaseError):
            _parse_single_date(date_string, Era.CE)


if __name__ == "__main__":
    pytest.main([__file__])
