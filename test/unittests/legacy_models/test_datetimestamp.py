import pytest

from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.datetimestamp import create_date_time_stamp


class TestCreateDateTimeStamp:
    """Tests for the create_date_time_stamp factory function."""

    def test_invalid_format_raises(self) -> None:
        # Validates regex-based parsing logic
        with pytest.raises(BaseError, match="Invalid xsd:dateTimeStamp"):
            create_date_time_stamp("not-a-timestamp")

    def test_invalid_format_missing_timezone(self) -> None:
        # Timezone is required for xsd:dateTimeStamp
        with pytest.raises(BaseError, match="Invalid xsd:dateTimeStamp"):
            create_date_time_stamp("2024-01-15T10:30:00")


class TestDateTimeStampEquality:
    """Tests for DateTimeStamp custom __eq__ implementation."""

    def test_equality_with_string(self) -> None:
        # Custom __eq__ allows comparison with string
        ts = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert ts == "2024-01-15T10:30:00Z"

    def test_equality_with_another_datetimestamp(self) -> None:
        ts1 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert ts1 == ts2

    def test_inequality(self) -> None:
        ts1 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-16T10:30:00Z")
        assert ts1 != ts2

    def test_equality_with_incompatible_type(self) -> None:
        ts = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert (ts == 123) is False


class TestDateTimeStampOrdering:
    """Tests for DateTimeStamp custom comparison operators from @total_ordering."""

    def test_less_than_with_string(self) -> None:
        ts = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert ts < "2024-01-16T10:30:00Z"

    def test_less_than_with_another_datetimestamp(self) -> None:
        ts1 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-16T10:30:00Z")
        assert ts1 < ts2

    def test_greater_than(self) -> None:
        # @total_ordering derives > from <
        ts1 = create_date_time_stamp("2024-01-16T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert ts1 > ts2

    def test_less_than_or_equal(self) -> None:
        # @total_ordering derives <= from < and ==
        ts1 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-15T10:30:00Z")
        assert ts1 <= ts2


class TestDateTimeStampHashable:
    """Tests for DateTimeStamp hashability (needed for use in sets/dicts)."""

    def test_usable_in_set(self) -> None:
        ts1 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts2 = create_date_time_stamp("2024-01-15T10:30:00Z")
        ts_set = {ts1, ts2}
        # Two equal timestamps should deduplicate in a set
        assert len(ts_set) == 1

    def test_usable_as_dict_key(self) -> None:
        ts = create_date_time_stamp("2024-01-15T10:30:00Z")
        d = {ts: "value"}
        assert d[ts] == "value"
